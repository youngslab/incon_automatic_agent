from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pandas import DataFrame
from prettytable import PrettyTable


def report(token, channel, message):
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

def dataframe_to_prettytable(df: DataFrame) -> PrettyTable:
    """Convert a pandas DataFrame to a PrettyTable object."""
    pt = PrettyTable()
    pt.field_names = df.columns.tolist()
    pt.add_rows(df.values.tolist())
    return pt

def get_channel_id(client: WebClient, channel_name: str) -> str:
    """
    Get the Slack channel ID from the channel name.

    :param client: An instance of WebClient.
    :param channel_name: The name of the channel (e.g., '#general').
    :return: The channel ID as a string.
    """
    try:
        # 채널 리스트 가져오기
        response = client.conversations_list()
        channels = response["channels"]

        # 채널 이름으로 ID 찾기
        for channel in channels:
            if channel["name"] == channel_name.lstrip("#"):  # '#' 제거 후 비교
                return channel["id"]

        print(f"Channel '{channel_name}' not found.")
        return None
    except SlackApiError as e:
        error = e.response.get('error', 'Unknown error')
        print(f"Error fetching channels: {error}")
        return None



class SlackReporter:
    def __init__(self, slack_token: str, channel: str):
        """Initialize the SlackReporter with a token and channel name."""
        self.client = WebClient(token=slack_token)
        self.channel = channel

    def send_message(self, message: str) -> bool:
        """Send a simple text message to the Slack channel."""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message
            )
            return response["ok"]
        except SlackApiError as e:
            error = e.response.get('error', 'Unknown error')
            print(f"Error sending message to {self.channel}: {error}")
            return False

    def send_dataframe(self, df: DataFrame) -> bool:
        """Send a DataFrame as a PrettyTable string to the Slack channel."""
        try:
            table_str = str(dataframe_to_prettytable(df))
            return self.send_message(table_str)
        except Exception as e:
            print(f"Error converting DataFrame to table: {e}")
            return False

    def send_file(self, file_path: str, title: str = None, initial_comment: str = None) -> bool:
        """
        Send a file to the Slack channel using files_upload_v2.

        :param file_path: Path to the file to send.
        :param title: Optional title for the uploaded file.
        :param initial_comment: Optional initial comment to add with the file.
        :return: True if the file was successfully sent, False otherwise.
        """
        try:
            with open(file_path, 'rb') as file_content:
                response = self.client.files_upload_v2(
                    channel= get_channel_id(self.client, self.channel),
                    file=file_content,
                    filename=file_path.split('/')[-1],
                    title=title,
                    initial_comment=initial_comment
                )
                return response["ok"]
        except SlackApiError as e:
            error = e.response.get('error', 'Unknown error')
            print(f"Error sending file to {self.channel}: {error}")
            return False
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False
        except Exception as e:
            print(f"Unexpected error sending file: {e}")
            return False
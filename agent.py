
import sys, time
import traceback
from data.incon import Incon
from market.g2b import G2B

from res.resource_manager import resource_manager as resmgr

settings_enable_pres = True
settings_enable_bids = True

def create_data_provider():
    # create incon object
    id = resmgr.get_account("incon","id")
    pw = resmgr.get_account("incon","pw")
    return Incon(id, pw, headless=False)

def create_markets() -> dict:
    markets = dict()       
    pw = resmgr.get_account("g2b","pw")
    rn = resmgr.get_account("g2b","rn")
    markets['나라장터'] = G2B(pw, rn)
    return markets

def main():
    try:
        dp = create_data_provider()
        ms = create_markets()

        if settings_enable_pres:
            pres = dp.get_pre_data()
            for pre in pres:
                market = ms.get(pre.market)
                if not market:                    
                    continue

                if pre.is_completed():
                    continue

                if market.register(pre):
                    pre.complete()
                    time.sleep(0.1)
                    if not pre.is_completed():
                        raise Exception(f"agent) Clicked But Not Completed {pre.number}")
                    print(f"agent) Registered {pre.number} - {pre.title} ")

        if settings_enable_bids:     
            bids = dp.get_bid_data()
            for bid in bids:                
                market = ms.get(bid.market)
                if not market:
                    continue

                if bid.is_completed():
                    continue

                if not bid.is_ready:
                    continue

                success, message = market.participate(bid)
                if success:                    
                    bid.complete()
                    print(f"agent) Registered {bid.number} - {bid.title} ")
                else:
                    print(f"agent) Can not participate in {bid.number}, {bid.title} - {message}")

    except Exception as e:        
        traceback.print_exception(*sys.exc_info())

if __name__ == "__main__":    
    main()

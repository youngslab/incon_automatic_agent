import datetime
import os

from org.kogas.kogas import Foo



# 객체 생성
# obj =  os.path.dirname('foo')
obj =  Foo()

# 객체의 클래스가 정의된 모듈의 전체 이름
class_name = obj.__class__.__name__
module_name = obj.__class__.__module__

# 패키지 이름 추출
package_name = module_name.split('.')[0]


print(f"클래스 이름: {class_name}")
print(f"모듈 이름: {module_name}")
print(f"패키지 이름: {package_name}")


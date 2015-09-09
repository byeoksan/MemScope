
from core.config import *
from core.mm.user import *
from core.vmarea import *
from core.task import *
from core.file import *

for cls in STRUCTS.values():
  cls.initclass()


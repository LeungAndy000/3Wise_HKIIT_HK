from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from wisemessage.config import MessageConfig
from wisemessage.runtime import configure_runtime
from wisemessage.tokenizer import MessageTokenizer
ms=configure_runtime('CPU')
from wisemessage.model import MessageClassifier
from pathlib import Path
import numpy as np
root=Path('artifacts/pretrained')
c=MessageConfig.from_json(root/'config.json')
m=MessageClassifier(c)
print('LOAD',ms.load_param_into_net(m,ms.load_checkpoint(str(root/'model.ckpt')),strict_load=True))
m.set_train(False)
t=MessageTokenizer(root/'vocab.txt',max_length=64)
e=t.encode_batch(['您好，请查收验证码。','阿媽，我換咗電話，急需你轉錢。','Your OTP 驗證碼123456。'])
y=m(*(ms.Tensor(e[k],ms.int32) for k in ('input_ids','attention_mask','token_type_ids'))).asnumpy()
print('PARAMETERS',sum(np.prod(p.shape) for p in m.get_parameters()),'OUTPUT_SHAPE',y.shape,'FINITE',np.isfinite(y).all(),'VOCAB',t.vocab_size)
print('TOKEN_TYPES_ZERO',np.all(e['token_type_ids']==0))

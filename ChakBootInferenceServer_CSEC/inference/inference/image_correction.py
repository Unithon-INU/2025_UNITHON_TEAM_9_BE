import torch
from PIL import Image
import torchvision.transforms as T
import hydra
from omegaconf import open_dict
from .utils.util import parse_config
from .model.csecnet import LitModel
from globalenv import *

# ────────────────── Singleton Enhancer ──────────────────
from hydra import initialize, compose

class _CSECEnhancer:
    def __init__(self):
        # 1. 설정 로드 (버전 호환 방식)
        with initialize(config_path="config"):
            cfg = compose(config_name="config")
        opt = parse_config(cfg, TEST)
        with open_dict(opt):
            opt[MODE] = TEST

        # 2. 체크포인트 로드 (GPU에 올림)
        ckpt_path = opt[CHECKPOINT_PATH]
        self.model = LitModel.load_from_checkpoint(ckpt_path, opt=opt)
        self.model.eval().cuda()

        # 3. 전‧후처리 파이프라인
        self.to_tensor = T.Compose([T.Resize((512, 512)), T.ToTensor()])
        self.to_pil = T.ToPILImage()

    @torch.no_grad()
    def __call__(self, img: Image.Image) -> Image.Image:
        """단일 PIL 이미지를 보정하여 PIL로 반환"""
        x = self.to_tensor(img).unsqueeze(0).cuda()       # [1,3,H,W]
        y = self.model(x)                                 # 0-1 범위
        return self.to_pil(y.squeeze(0).cpu().clamp(0, 1))


# ────────────────── 외부 공개 함수 ──────────────────
_enhancer = None  # 첫 호출 시에만 모델을 메모리에 올림
def enhance(img: Image.Image) -> Image.Image:
    global _enhancer
    if _enhancer is None:
        _enhancer = _CSECEnhancer()
    return _enhancer(img)

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
        self.to_tensor = T.ToTensor()
        self.to_pil = T.ToPILImage()

    @torch.no_grad()
    def __call__(self, img: Image.Image) -> Image.Image:
        """단일 PIL 이미지를 보정하여 PIL로 반환"""
        x = self.to_tensor(img).unsqueeze(0).cuda()      # [1,3,H,W]
        y = self.model(x)                                # 0-1 범위
        return self.to_pil(y.squeeze(0).cpu().clamp(0, 1))


# ────────────────── 외부 공개 함수 (수정됨) ──────────────────
_enhancer = None  # 첫 호출 시에만 모델을 메모리에 올림

def enhance(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """
    이미지를 보정하며, 보정 강도를 조절할 수 있습니다.

    Args:
        img (Image.Image): 보정할 원본 PIL 이미지.
        strength (float): 보정 강도. 0.0은 원본, 1.0은 완전 보정. (기본값: 1.0)

    Returns:
        Image.Image: 보정된 PIL 이미지.
    """
    global _enhancer
    if _enhancer is None:
        _enhancer = _CSECEnhancer()

    # strength 값 유효성 검사
    if not 0.0 <= strength <= 1.0:
        raise ValueError("Strength 값은 0.0과 1.0 사이여야 합니다.")

    # strength가 0이면 원본 이미지를 그대로 반환
    if strength == 0.0:
        return img

    # 모델을 통해 100% 보정된 이미지를 생성
    enhanced_img = _enhancer(img)

    # strength가 1이면 완전히 보정된 이미지를 반환
    if strength == 1.0:
        return enhanced_img
    
    # 원본과 보정된 이미지를 strength 비율로 블렌딩
    # Image.blend(img1, img2, alpha) => img1 * (1 - alpha) + img2 * alpha
    return Image.blend(img, enhanced_img, alpha=strength)
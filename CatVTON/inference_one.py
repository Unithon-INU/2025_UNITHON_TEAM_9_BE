import os

import numpy as np
import torch
from PIL import Image
from diffusers.image_processor import VaeImageProcessor
from huggingface_hub import snapshot_download

from model.cloth_masker import AutoMasker, vis_mask
from model.pipeline import CatVTONPipeline
from utils import init_weight_dtype, resize_and_crop, resize_and_padding

# DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else 'cpu')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


repo_path = snapshot_download(repo_id="zhengchong/CatVTON")
# print('repo path:', repo_path)

# Pipeline
pipeline = CatVTONPipeline(
    base_ckpt="booksforcharlie/stable-diffusion-inpainting",
    attn_ckpt=repo_path,
    attn_ckpt_version="mix",
    weight_dtype=init_weight_dtype("bf16"),
    use_tf32=True,
    device=DEVICE,
    skip_safety_check=True
)
# AutoMasker
mask_processor = VaeImageProcessor(vae_scale_factor=8, do_normalize=False, do_binarize=True, do_convert_grayscale=True)
automasker = AutoMasker(
    densepose_ckpt=os.path.join(repo_path, "DensePose"),
    schp_ckpt=os.path.join(repo_path, "SCHP"),
    device=DEVICE,
)


WIDTH = 768
HEIGHT = 1024


def inference_model(
    person_image,  # numpy image
    cloth_image,  # numpy image
    cloth_type='upper',
    num_inference_steps=50,
    guidance_scale=2.95,
    seed=42,
    show_type="result only",
):
    generator = None
    if seed != -1:
        generator = torch.Generator(device=DEVICE).manual_seed(seed)

    # person_image = Image.open(person_image).convert("RGB")
    # cloth_image = Image.open(cloth_image).convert("RGB")
    person_image = resize_and_crop(person_image, (WIDTH, HEIGHT))
    cloth_image = resize_and_padding(cloth_image, (WIDTH, HEIGHT))
    
    # Process mask
    mask = automasker(
        person_image,
        cloth_type
    )['mask']
    mask = mask_processor.blur(mask, blur_factor=9)
    # print('mask inference')

    # Inference
    # try:
    result_image = pipeline(
        image=person_image,
        condition_image=cloth_image,
        mask=mask,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator,
    )[0]
    # print('inference')
    # except Exception as e:
    #     raise gr.Error(
    #         "An error occurred. Please try again later: {}".format(e)
    #     )

    # save_result_image = image_grid([person_image, masked_person, cloth_image, result_image], 1, 4)
    # save_result_image.save(result_save_path)
    if show_type == "result only":
        return result_image
    else:
        # Post-process
        masked_person = vis_mask(person_image, mask)
        width, height = person_image.size
        if show_type == "input & result":
            condition_width = width // 2
            conditions = image_grid([person_image, cloth_image], 2, 1)
        else:
            condition_width = width // 3
            conditions = image_grid([person_image, masked_person , cloth_image], 3, 1)
        conditions = conditions.resize((condition_width, height), Image.NEAREST)
        new_result_image = Image.new("RGB", (width + condition_width + 5, height))
        new_result_image.paste(conditions, (0, 0))
        new_result_image.paste(result_image, (condition_width + 5, 0))
    return new_result_image


def main():
    person_image_path = 'my_test/wonyeong.png'
    cloth_image_path = 'my_test/cloth12.png'
    result_image_path = 'my_test/result.jpg'

    blank_mask_path = 'my_test/blank_mask.png'

    cloth_type = 'upper'  # upper, lower, overall
    num_inference_steps = 25
    guidance_scale = 3
    seed = 42
    show_type = 'input & mask & result'

    blank_mask = Image.fromarray(np.zeros((1, 1), dtype=np.uint8))  # 완전 검정
    blank_mask.save(blank_mask_path)

    result_image = inference_model(
        Image.open(person_image_path).convert('RGB'),
        Image.open(cloth_image_path).convert('RGB'),
        cloth_type,
        num_inference_steps,
        guidance_scale,
        seed,
        show_type
    )

    result_image.show()
    result_image.save(result_image_path)


if __name__ == '__main__':
    main()

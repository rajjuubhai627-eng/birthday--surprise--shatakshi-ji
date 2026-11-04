import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import imageio

def create_cinematic_video():
    fps = 24
    width, height = 1280, 720
    
    # Load images
    img1 = Image.open('car_closed.jpg').convert('RGB')
    img2 = Image.open('car_boot_surprise.jpg').convert('RGB')
    img3 = Image.open('cake_cutting.jpg').convert('RGB')
    
    def prepare_base(img):
        # Resize to fill 1280x720 with aspect ratio preserved
        img_ratio = img.width / img.height
        target_ratio = width / height
        if img_ratio > target_ratio:
            new_h = height
            new_w = int(height * img_ratio)
        else:
            new_w = width
            new_h = int(width / img_ratio)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        # Center crop
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        return resized.crop((left, top, left + width, top + height))

    base1 = prepare_base(img1)
    base2 = prepare_base(img2)
    base3 = prepare_base(img3)

    frames = []

    # Helper for smooth pan/zoom (Ken Burns effect)
    def render_ken_burns(base, start_zoom, end_zoom, num_frames, overlay_text=None, subtitle=None):
        out = []
        for i in range(num_frames):
            t = i / max(1, num_frames - 1)
            # Smooth ease-in-out
            ease_t = 0.5 - 0.5 * np.cos(np.pi * t)
            zoom = start_zoom + (end_zoom - start_zoom) * ease_t
            
            # Crop zoomed area from base
            crop_w = int(width / zoom)
            crop_h = int(height / zoom)
            crop_x = (width - crop_w) // 2
            crop_y = (height - crop_h) // 2
            
            frame_cropped = base.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
            frame_resized = frame_cropped.resize((width, height), Image.Resampling.BILINEAR)

            # Draw cinematic text overlay if requested
            if overlay_text:
                draw = ImageDraw.Draw(frame_resized, 'RGBA')
                # Lower third subtle gradient
                for y in range(height - 120, height):
                    alpha = int(180 * ((y - (height - 120)) / 120))
                    draw.line([(0, y), (width, y)], fill=(7, 11, 20, alpha))
            
            out.append(np.array(frame_resized))
        return out

    print("Rendering Scene 1: Closed car...")
    scene1_frames = render_ken_burns(base1, 1.0, 1.08, fps * 4) # 4 seconds

    print("Rendering Scene 2: Open boot with cake & balloons...")
    scene2_frames = render_ken_burns(base2, 1.02, 1.10, fps * 5) # 5 seconds

    print("Rendering Scene 3: Cake cutting celebration...")
    scene3_frames = render_ken_burns(base3, 1.05, 1.14, fps * 5) # 5 seconds

    # Crossfade helper
    def crossfade(scene_a, scene_b, fade_len):
        crossfaded = []
        for i in range(fade_len):
            alpha = (i + 1) / (fade_len + 1)
            f_a = scene_a[-fade_len + i].astype(np.float32)
            f_b = scene_b[i].astype(np.float32)
            blended = ((1 - alpha) * f_a + alpha * f_b).astype(np.uint8)
            crossfaded.append(blended)
        return scene_a[:-fade_len] + crossfaded + scene_b[fade_len:]

    fade_frames = fps * 1  # 1 sec crossfade
    print("Blending transitions...")
    video_frames = crossfade(scene1_frames, scene2_frames, fade_frames)
    video_frames = crossfade(video_frames, scene3_frames, fade_frames)

    print(f"Total frames: {len(video_frames)}, Duration: {len(video_frames)/fps:.1f}s")
    
    # Save as MP4
    output_path = 'birthday_surprise.mp4'
    writer = imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p')
    for f in video_frames:
        writer.append_data(f)
    writer.close()
    print("Video rendered successfully to:", output_path)

if __name__ == '__main__':
    create_cinematic_video()


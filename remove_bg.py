import sys
from PIL import Image

def remove_background(image_path, output_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        # Get the background color from the top-left pixel
        bg_color = data[0]
        
        new_data = []
        # Tolerance for background color
        tolerance = 30
        
        for item in data:
            if (abs(item[0] - bg_color[0]) < tolerance and
                abs(item[1] - bg_color[1]) < tolerance and
                abs(item[2] - bg_color[2]) < tolerance):
                # Replace background with transparent
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        img.save(output_path, "PNG")
        print(f"Successfully processed {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        remove_background(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python remove_bg.py <input> <output>")

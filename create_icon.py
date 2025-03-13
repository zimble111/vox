from PIL import Image, ImageDraw


def create_icon():
    # Размер иконки: 256x256 пикселей
    size = (256, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Рисуем круг (например, синим цветом)
    circle_center = (size[0] // 2, size[1] // 2)
    circle_radius = 100
    draw.ellipse(
        [
            circle_center[0] - circle_radius, circle_center[1] - circle_radius,
            circle_center[0] + circle_radius, circle_center[1] + circle_radius
        ],
        fill=(0, 123, 255, 255)
    )

    # Сохраняем как ICO
    image.save("icon.icns", format="ICO")
    print("Icon saved as icon.icns")


if __name__ == '__main__':
    create_icon()

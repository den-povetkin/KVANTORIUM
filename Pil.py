from PIL import Image

def advanced_dithering(input_path, output_path, dot_size=2, contrast=1.0):
    """
    Расширенная версия с настраиваемым размером точек и контрастом
    """
    # Открываем и обрабатываем изображение
    img = Image.open(input_path)
    
    # Конвертируем в черно-белое с настройкой контраста
    img = img.convert('L')
    
    # Увеличиваем контраст
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    
    # Увеличиваем размер для создания точек
    if dot_size > 1:
        large_size = (img.width * dot_size, img.height * dot_size)
        img = img.resize(large_size, Image.NEAREST)
    
    # Применяем дизеринг
    img = img.convert('1')
    
    # Возвращаем к исходному размеру
    if dot_size > 1:
        original_size = (img.width // dot_size, img.height // dot_size)
        img = img.resize(original_size, Image.NEAREST)
    
    img.save(output_path)
    print(f"Изображение с точечным эффектом сохранено: {output_path}")

# Пример использования расширенной версии
advanced_dithering("input.jpg", "output_advanced.png", dot_size=3, contrast=1.5)
#!/usr/bin/env python3
"""
Тесты сжатия картинок без потери качества перед сборкой PDF.

Проверяется, что:
  1. PNG пересжимается lossless: пиксели не меняются, файл становится меньше.
  2. PNG с прозрачностью сохраняет альфа-канал без искажений.
  3. JPEG не перекодируется (байты не меняются) — качество не теряется.
  4. Итоговый PDF получается меньше, если PNG был сжат.
  5. Эндпоинт /api/images-to-pdf собирает валидный PDF из нескольких картинок
     и встраивает JPEG без пересжатия.

Запуск: python3 test_lossless_compression.py
Скрипт не требует запущенного сервера (используется Flask test client).
"""

import os
import sys
import tempfile

import img2pdf
from PIL import Image, ImageDraw

from app import app, compress_image_lossless


def create_test_images(directory):
    """Создаёт набор тестовых картинок разных форматов."""
    images = {}

    # RGB PNG, сохранённый с быстрым (неоптимальным) сжатием
    rgb = Image.new('RGB', (800, 600), (255, 255, 255))
    draw = ImageDraw.Draw(rgb)
    for i in range(0, 800, 20):
        draw.line([(i, 0), (i, 600)], fill=(i % 256, 200, 100))
    draw.text((350, 300), 'Test RGB PNG')
    images['rgb_png'] = os.path.join(directory, 'rgb.png')
    rgb.save(images['rgb_png'], 'PNG', compress_level=1)

    # RGBA PNG с полупрозрачной фигурой
    rgba = Image.new('RGBA', (800, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rgba)
    draw.ellipse((100, 100, 700, 500), fill=(30, 144, 255, 128))
    draw.text((350, 300), 'Test RGBA PNG')
    images['rgba_png'] = os.path.join(directory, 'rgba.png')
    rgba.save(images['rgba_png'], 'PNG', compress_level=1)

    # JPEG
    jpeg = Image.new('RGB', (800, 600), (73, 109, 137))
    draw = ImageDraw.Draw(jpeg)
    for i in range(50):
        draw.line([(i * 16, 0), (0, i * 12)], fill=(255, 255, 255))
    draw.text((350, 300), 'Test JPEG')
    images['jpeg'] = os.path.join(directory, 'photo.jpg')
    jpeg.save(images['jpeg'], 'JPEG', quality=85)

    return images


def pixels_identical(path_a, path_b):
    """True, если размер, режим и все пиксели (включая альфу) совпадают."""
    with Image.open(path_a) as first, Image.open(path_b) as second:
        if first.size != second.size or first.mode != second.mode:
            return False
        return first.tobytes() == second.tobytes()


def mimetype_for(path):
    """MIME-тип для тестового файла."""
    if path.lower().endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    return 'image/png'


def test_png_compressed_lossless():
    """PNG сжимается lossless: пиксели те же, размер файла меньше."""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = create_test_images(temp_dir)
        source = images['rgb_png']

        compressed = compress_image_lossless(source, temp_dir, 1)

        assert compressed != source, 'PNG должен быть пересжат в отдельный файл'
        assert pixels_identical(source, compressed), 'Пиксели PNG изменились!'
        assert os.path.getsize(compressed) < os.path.getsize(source), \
            'Размер PNG не уменьшился'

        print(
            f'   ✓ PNG: {os.path.getsize(source)} -> '
            f'{os.path.getsize(compressed)} байт, пиксели идентичны'
        )


def test_png_with_alpha_stays_lossless():
    """PNG с прозрачностью сохраняет альфа-канал без искажений."""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = create_test_images(temp_dir)
        source = images['rgba_png']

        compressed = compress_image_lossless(source, temp_dir, 1)

        assert pixels_identical(source, compressed), \
            'Пиксели или альфа-канал RGBA PNG изменились!'
        with Image.open(compressed) as image:
            assert image.mode == 'RGBA', 'Потерян альфа-канал (режим RGBA)'

        print(
            f'   ✓ RGBA PNG: {os.path.getsize(source)} -> '
            f'{os.path.getsize(compressed)} байт, альфа-канал сохранён'
        )


def test_jpeg_is_not_reencoded():
    """JPEG отдаётся без перекодирования — качество не меняется."""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = create_test_images(temp_dir)
        source = images['jpeg']

        with open(source, 'rb') as file:
            original_bytes = file.read()

        result = compress_image_lossless(source, temp_dir, 1)

        assert result == source, 'JPEG не должен перекодироваться'
        with open(result, 'rb') as file:
            assert file.read() == original_bytes, 'Байты JPEG изменились!'

        print('   ✓ JPEG: файл отдан без перекодирования, байты не изменились')


def test_pdf_size_reduced_by_lossless_png():
    """Lossless-сжатие PNG уменьшает итоговый PDF."""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = create_test_images(temp_dir)
        compressed = compress_image_lossless(images['rgb_png'], temp_dir, 1)

        pdf_from_original = img2pdf.convert([images['rgb_png']])
        pdf_from_compressed = img2pdf.convert([compressed])

        assert pdf_from_compressed[:4] == b'%PDF', 'Получился не PDF'
        assert len(pdf_from_compressed) < len(pdf_from_original), \
            'PDF не уменьшился после сжатия PNG'

        print(
            f'   ✓ PDF: {len(pdf_from_original)} -> '
            f'{len(pdf_from_compressed)} байт'
        )


def test_api_returns_valid_pdf_without_reencoding():
    """Эндпоинт собирает валидный PDF и встраивает JPEG без пересжатия."""
    with tempfile.TemporaryDirectory() as temp_dir:
        images = create_test_images(temp_dir)

        handles = []
        files = []
        for path in images.values():
            handle = open(path, 'rb')
            handles.append(handle)
            files.append((handle, os.path.basename(path), mimetype_for(path)))

        try:
            client = app.test_client()
            response = client.post(
                '/api/images-to-pdf',
                data={'files': files},
                content_type='multipart/form-data'
            )
        finally:
            for handle in handles:
                handle.close()

        assert response.status_code == 200, \
            f'Ожидался статус 200, получен {response.status_code}'
        assert response.mimetype == 'application/pdf', \
            f'Ожидался application/pdf, получен {response.mimetype}'
        assert response.data[:4] == b'%PDF', 'Тело ответа не является PDF'

        # JPEG внутри PDF должен быть исходным, без перекодирования
        with open(images['jpeg'], 'rb') as file:
            jpeg_bytes = file.read()
        assert jpeg_bytes[200:400] in response.data, \
            'JPEG внутри PDF был перекодирован'

        print(
            f'   ✓ Эндпоинт вернул PDF {len(response.data)} байт, '
            'JPEG встроен без пересжатия'
        )


def main():
    """Запускает все тесты и печатает результат."""
    tests = [
        ('1. Lossless-сжатие PNG', test_png_compressed_lossless),
        ('2. PNG с прозрачностью', test_png_with_alpha_stays_lossless),
        ('3. JPEG без перекодирования', test_jpeg_is_not_reencoded),
        ('4. Размер PDF после сжатия PNG', test_pdf_size_reduced_by_lossless_png),
        ('5. Эндпоинт /api/images-to-pdf', test_api_returns_valid_pdf_without_reencoding),
    ]

    print('\n' + '=' * 60)
    print('Тесты lossless-сжатия картинок перед сборкой PDF')
    print('=' * 60)

    failed = 0
    for title, test in tests:
        print(f'\n{title}')
        try:
            test()
        except AssertionError as error:
            failed += 1
            print(f'   ✗ Провалено: {error}')
        except Exception as error:  # noqa: BLE001 - тестовый скрипт
            failed += 1
            print(f'   ✗ Ошибка {type(error).__name__}: {error}')

    print('\n' + '=' * 60)
    if failed:
        print(f'✗ Провалено тестов: {failed} из {len(tests)}')
    else:
        print(f'✓ Все тесты пройдены: {len(tests)} из {len(tests)}')
    print('=' * 60)

    return failed


if __name__ == '__main__':
    sys.exit(main())

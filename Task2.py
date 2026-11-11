from abc import ABC, abstractmethod
import unittest
import zlib

# 1. Абстрактный интерфейс потока чтения
class IReadableStream(ABC):
    @abstractmethod
    def read(self, size: int = -1) -> bytes:
        """Считывает порцию данных заданного размера (-1 — до конца)."""
        pass

# 2. Конкретный компонент (источник — чтение из файла/памяти по частям)
class FileStream(IReadableStream):
    def __init__(self, data: bytes, chunk_size: int = 16) -> None:
        self._data: bytes = data
        self._offset: int = 0
        self._chunk_size: int = chunk_size

    def read(self, size: int = -1) -> bytes:
        if self._offset >= len(self._data):
            return b""

        end = len(self._data) if size < 0 else min(self._offset + size, len(self._data))
        chunk = self._data[self._offset:end]
        self._offset = end
        return chunk



# 3. Базовый декоратор потока
class StreamDecorator(IReadableStream, ABC):
    def __init__(self, stream: IReadableStream) -> None:
        self._stream: IReadableStream = stream

    @abstractmethod
    def read(self, size: int = -1) -> bytes:
        pass


# 4. Конкретные декораторы (работают в потоковом режиме)
class DecryptionStream(StreamDecorator):
    """Декоратор расшифровки (XOR-преобразование потока байт)."""

    def __init__(self, stream: IReadableStream, key: int = 42) -> None:
        super().__init__(stream)
        self._key: int = key

    def read(self, size: int = -1) -> bytes:
        encrypted_chunk = self._stream.read(size)
        if not encrypted_chunk:
            return b""
        return bytes(b ^ self._key for b in encrypted_chunk)


class DecompressionStream(StreamDecorator):
    """Декоратор распаковки сжатых данных (потоковый zlib)."""

    def __init__(self, stream: IReadableStream) -> None:
        super().__init__(stream)
        self._dobj = zlib.decompressobj()
        self._eof_reached = False

    def read(self, size: int = -1) -> bytes:
        # Поскольку размер сжатых чанков не равен размеру распакованных,
        # читаем нижележащий поток до тех пор, пока декомпрессор не выдаст данные.
        while not self._eof_reached:
            chunk = self._stream.read(size)
            if not chunk:
                # Больше нет данных, сбрасываем остатки буфера декомпрессора
                self._eof_reached = True
                return self._dobj.flush()

            decompressed = self._dobj.decompress(chunk)
            if decompressed:
                return decompressed

        return self._dobj.flush()


class ChecksumStream(StreamDecorator):
    """Декоратор подсчёта контрольной суммы (CRC32) на лету."""

    def __init__(self, stream: IReadableStream) -> None:
        super().__init__(stream)
        self.checksum: int = 0

    def read(self, size: int = -1) -> bytes:
        data = self._stream.read(size)
        if data:
            self.checksum = zlib.crc32(data, self.checksum)
        return data



# 5. Юнит-тесты
class TestBackupStreamDecorator(unittest.TestCase):

    def test_streaming_decryption_and_decompression(self) -> None:
        raw_data = b"Streaming data verification text for backup system." * 5
        compressed = zlib.compress(raw_data)
        encrypted = bytes(b ^ 88 for b in compressed)

        # Сборка цепочки через декораторы (с маленьким размером чанка для проверки итераций)
        stream: IReadableStream = FileStream(encrypted, chunk_size=8)
        stream = DecryptionStream(stream, key=88)
        stream = DecompressionStream(stream)

        # Сборка всех чанков обратно в один результат
        result = bytearray()
        while True:
            chunk = stream.read(10)
            if not chunk:
                break
            result.extend(chunk)

        self.assertEqual(bytes(result), raw_data)

    def test_checksum_difference(self) -> None:
        raw_data = b"Important database state bytes..."
        compressed = zlib.compress(raw_data)
        encrypted = bytes(b ^ 55 for b in compressed)

        # Чексумма ДО распаковки (на зашифрованных данных)
        s1 = FileStream(encrypted)
        dec1 = DecryptionStream(s1, key=55)
        chk_before = ChecksumStream(dec1)
        decomp1 = DecompressionStream(chk_before)

        while decomp1.read(): pass  # вычитываем до конца

        # Чексумма ПОСЛЕ распаковки (на чистых данных)
        s2 = FileStream(encrypted)
        dec2 = DecryptionStream(s2, key=55)
        decomp2 = DecompressionStream(dec2)
        chk_after = ChecksumStream(decomp2)

        while chk_after.read(): pass  # вычитываем до конца
        self.assertNotEqual(chk_before.checksum, chk_after.checksum)
        self.assertEqual(chk_after.checksum, zlib.crc32(raw_data))



# 6. Запуск
if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
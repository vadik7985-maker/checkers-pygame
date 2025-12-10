import unittest
import sys

class TestSkipExamples(unittest.TestCase):
    @unittest.skip("Тест временно отключен - требует доработки логики")
    def test_not_implemented(self):
        """Пример пропуска теста"""
        self.fail("Этот тест не должен выполняться")
    
    @unittest.skipIf(sys.platform == "win32", "Тест не поддерживается в Windows")
    def test_platform_specific(self):
        """Пропуск на определенной платформе"""
        pass
    
    @unittest.skipUnless(sys.version_info >= (3, 7), "Требуется Python 3.7+")
    def test_python_version(self):
        """Проверка версии Python"""
        self.assertTrue(True)
    
    @unittest.expectedFailure
    def test_known_bug(self):
        """Тест для известной ошибки (ожидается падение)"""
        # TODO: Исправить в следующем релизе
        self.assertEqual(1, 2)  # Ожидаемо падает
    
    def test_normal_case(self):
        """Нормальный тест"""
        self.assertEqual(2 + 2, 4)

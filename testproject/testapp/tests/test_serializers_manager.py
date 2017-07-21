from django.test.testcases import SimpleTestCase
import djoser.serializers

from .common import mock


class SerializersManagerTest(SimpleTestCase):

    def test_serializer_manager_init(self):
        serializers_manager = djoser.serializers.SerializersManager({})
        self.assertFalse(serializers_manager.serializers)

    def test_get_serializer_non_proper_name(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer
        })
        self.assertRaises(Exception, serializers_manager.get, 'bad_name')

    def test_get(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer})
        serializer_class = serializers_manager.get('user')
        self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))

    def test_get_from_cache(self):
        serializers_manager = djoser.serializers.SerializersManager({
            'user': djoser.serializers.UserSerializer})
        serializer_class = serializers_manager.get('user')
        self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))

        with mock.patch('django.utils.module_loading.import_string') as import_string_mock:
            serializer_class = serializers_manager.get('user')
            self.assertTrue(issubclass(serializer_class, djoser.serializers.UserSerializer))
            self.assertFalse(import_string_mock.called)

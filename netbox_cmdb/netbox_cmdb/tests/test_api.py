from dcim.models.devices import Device, DeviceRole, DeviceType, Manufacturer
from dcim.models.sites import Site
from django.test import override_settings
from django.urls import reverse
from netbox.config import get_config
from rest_framework import status
from utilities.testing import APITestCase

from netbox_cmdb.models.prefix_list import PrefixList

# Test cases taken from unmerged PR https://github.com/netbox-community/netbox/pull/10764/
# except that we test it against a view from the CMDB

class APICursorPaginationTestCase(APITestCase):
    user_permissions = ('netbox_cmdb.view_prefixlist',)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('plugins-api:netbox_cmdb-api:prefixlist-list') + "?pagination_mode=cursor"
        cls.initial_record_count = 100

        site = Site.objects.create(name="SiteTest", slug="site-test")
        manufacturer = Manufacturer.objects.create(name="test", slug="test")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="model-test", slug="model-test"
        )
        device_role = DeviceRole.objects.create(name="role-test", slug="role-test")
        cls.device = Device.objects.create(
            name="router-test",
            device_role=device_role,
            device_type=device_type,
            site=site,
        )
        # Create a large number of Prefix list for testing
        PrefixList.objects.bulk_create([
            PrefixList(name=f'PF-{i}', device=cls.device) for i in range(1, 1 + cls.initial_record_count)
        ])

    def test_default_page_size(self):
        response = self.client.get(self.url, format='json', **self.header)
        page_size = get_config().PAGINATE_COUNT
        self.assertLess(page_size, self.initial_record_count, "Default page size not sufficient for data set")

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIn('cursor=', response.data['next'])
        self.assertIn('pagination_mode=cursor', response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), page_size)

    def test_custom_page_size(self):
        page_size = 10
        response = self.client.get(f'{self.url}&limit={page_size}', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIn('cursor=', response.data['next'])
        self.assertIn('pagination_mode=cursor', response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), page_size)

    @override_settings(MAX_PAGE_SIZE=20)
    def test_max_page_size(self):
        response = self.client.get(f'{self.url}&limit=0', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIn('cursor=', response.data['next'])
        self.assertIn('pagination_mode=cursor', response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 20)

    @override_settings(MAX_PAGE_SIZE=0)
    def test_max_page_size_disabled(self):
        response = self.client.get(f'{self.url}&limit=0', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), self.initial_record_count)

    def test_next_and_previous(self):
        page_size = 10
        page_1_response = self.client.get(f'{self.url}&limit={page_size}', format='json', **self.header)
        page_2_response = self.client.get(page_1_response.data['next'], format='json', **self.header)
        prev_response = self.client.get(page_2_response.data['previous'], format='json', **self.header)

        self.assertHttpStatus(page_2_response, status.HTTP_200_OK)
        self.assertEqual(len(page_2_response.data['results']), page_size)
        self.assertIsNotNone(page_2_response.data['next'])
        self.assertListEqual(page_1_response.data['results'], prev_response.data['results'])

    def test_invalid_cursor(self):
        response = self.client.get(f'{self.url}&cursor=invalid', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Invalid cursor')

    def test_ignore_invalid_page_size(self):
        response = self.client.get(f'{self.url}&limit=-1', format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), get_config().PAGINATE_COUNT)

    @override_settings(MAX_PAGE_SIZE=55)
    def test_delete_in_between(self):
        """
        CursorPagination should get all 101 objects even if one of the objects is deleted from page 1 during
        the process.
        """
        # create an extra record
        pf_to_delete = PrefixList.objects.create(name="PF-to-delete", device=self.device)
        try:
            page_1_response = self.client.get(f'{self.url}&limit=55', format='json', **self.header)
            pf_to_delete.delete()
        except Exception as e:
            pf_to_delete.delete()
            raise e

        page_2_response = self.client.get(page_1_response.data['next'], format='json', **self.header)

        self.assertHttpStatus(page_2_response, status.HTTP_200_OK)
        self.assertEqual(
            len(page_1_response.data['results']) + len(page_2_response.data['results']),
            self.initial_record_count + 1,
        )
        self.assertIsNone(page_2_response.data['next'])

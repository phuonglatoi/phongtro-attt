# ============================================
# apps/core/management/commands/create_test_data.py
# ============================================
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rooms.models import NhaTro, PhongTro
from faker import Faker

User = get_user_model()
fake = Faker('vi_VN')


class Command(BaseCommand):
    help = 'Tạo dữ liệu test'

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu test...')
        
        # Tạo users
        owner1 = User.objects.create_user(
            username='owner1',
            email='owner1@test.com',
            password='Test@123456',
            phone='0912345671',
            role='owner',
            is_verified=True
        )
        
        customer1 = User.objects.create_user(
            username='customer1',
            email='customer1@test.com',
            password='Test@123456',
            phone='0912345672',
            role='customer',
            is_verified=True
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Đã tạo users'))
        
        # Tạo nhà trọ
        nha_tro1 = NhaTro.objects.create(
            owner=owner1,
            ten_nha_tro='Nhà trọ ABC',
            dia_chi='123 Đường XYZ, Quận 1, TP.HCM',
            gia_dien='3500đ/kWh',
            gia_nuoc='20000đ/khối'
        )
        
        # Tạo phòng trọ
        for i in range(1, 11):
            PhongTro.objects.create(
                nha_tro=nha_tro1,
                ten_phong=f'Phòng {i}',
                dien_tich=f'{fake.random_int(15, 30)}m²',
                mo_ta=fake.text(200),
                gia_tien=fake.random_int(2000000, 5000000),
                so_nguoi_o=fake.random_int(1, 3)
            )
        
        self.stdout.write(self.style.SUCCESS('✅ Đã tạo 10 phòng trọ'))
        self.stdout.write(self.style.SUCCESS('Hoàn tất!'))
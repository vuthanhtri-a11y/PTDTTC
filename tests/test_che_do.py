import unittest

import lt_che_do as cd


def ngay(n):
    return [f"d{i:04d}" for i in range(n)]


class CheDoTests(unittest.TestCase):
    def test_bear_has_hysteresis(self):
        # Quyet dinh 2: vao GIAM khi < 0,97 x MA200; vung 0,97-1,00 GIU GIAM;
        # chi ra khi dong cua > MA200.
        c = [100.0] * 250 + [96.0] * 3 + [99.0] * 5 + [101.0] * 3
        st = cd.chuoi_che_do(c, [1000] * len(c))
        self.assertIsNone(st[198])
        self.assertEqual(st[249], 'DIEU_CHINH')      # di ngang = khong TANG
        self.assertEqual(st[250], 'GIAM')
        self.assertEqual(st[255], 'GIAM')            # doi xung se ra o day
        self.assertEqual(st[258], 'DIEU_CHINH')      # tren MA200, MA50 < MA200

    def test_uptrend_is_tang(self):
        c = [100 * 1.002 ** i for i in range(300)]
        self.assertEqual(cd.chuoi_che_do(c, [1000] * 300)[-1], 'TANG')

    def test_distribution_days_force_correction(self):
        c, v = [100.0], [1000]
        for i in range(1, 300):
            if i in (280, 284, 288, 292, 296):        # 5 phien phan phoi / 25
                c.append(c[-1] * 0.995)
                v.append(2000)
            else:
                c.append(c[-1] * 1.003)
                v.append(1000)
        self.assertEqual(len(cd.phien_phan_phoi(c, v, 299)), 5)
        self.assertEqual(cd.chuoi_che_do(c, v)[-1], 'DIEU_CHINH')
        self.assertEqual(cd.chuoi_che_do(c, [1000] * 300)[-1], 'TANG')

    def test_zone_keeps_previous_state_without_upgrade(self):
        # Tu TANG roi vao vung 0,97-1,00 x MA200 (KL thap -> khong phai phien phan
        # phoi, MA50 van > MA200) -> giu TANG; khong co cach nao TANG tu vung nay
        # neu truoc do la DIEU_CHINH.
        c = [100 * 1.002 ** i for i in range(300)]
        m = sum(c[-199:]) / 199
        c.append(0.985 * m)
        v = [1000] * 300 + [500]
        st = cd.chuoi_che_do(c, v)
        ma200 = sum(c[-200:]) / 200
        self.assertTrue(0.97 * ma200 < c[-1] < ma200)
        self.assertEqual(st[-2:], ['TANG', 'TANG'])

    def test_summary_and_ceiling(self):
        c = [100.0] * 250 + [96.0] * 3 + [99.0] * 5 + [101.0] * 3
        x = cd.tinh_che_do(ngay(len(c)), c, [1000] * len(c))
        self.assertEqual(x['che_do'], 'DIEU_CHINH')
        self.assertEqual(x['tran_co_phieu'], 0.60)
        self.assertEqual(x['tu_ngay'], 'd0258')
        self.assertEqual(x['so_phien'], 3)
        self.assertAlmostEqual(x['nguong_vao_giam'], round(0.97 * x['ma200'], 2), places=2)
        self.assertIn(('d0250', 'DIEU_CHINH', 'GIAM'), [tuple(d) for d in x['doi_gan_nhat']])
        self.assertIsNone(cd.tinh_che_do(ngay(150), [100.0] * 150, [1] * 150))

    def test_scan_without_index_series_is_unknown(self):
        self.assertIsNone(cd.tu_ban_quet({}))
        c = [100 * 1.002 ** i for i in range(300)]
        x = cd.tu_ban_quet({'_vnindex': {'t': ngay(300), 'c': c, 'v': [1000] * 300}})
        self.assertEqual(x['che_do'], 'TANG')


if __name__ == '__main__':
    unittest.main()

"""
Seed script — adds realistic dummy data for testing Moalidatna app.

Run in a NEW terminal (server can stay running):
  cd moalidatna-server
  python seed_data.py

Creates:
  - 2 generator accounts
  - 6 subscribers per generator
  - 2 workers per generator
  - 3 monthly budgets per generator
  - Receipts for most subscribers
"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'molidty_server.settings')

import django
django.setup()

from django.contrib.auth.hashers import make_password
from mainapp.models import Account, Subscriber, Worker, Budget, Receipt

# ── Helper ────────────────────────────────────────────────────────────────────
def log(msg): print(f"  {msg}")

# ── Clear existing seed data (idempotent) ─────────────────────────────────────
print("\n[1/6] Cleaning old seed data...")
Account.objects.filter(generator_name__in=['مولدة الكرخ', 'مولدة الرصافة']).delete()
print("  Done.")

# ── Generator Accounts ────────────────────────────────────────────────────────
print("\n[2/6] Creating generator accounts...")

gen1 = Account(
    generator_name='مولدة الكرخ',
    phone='07701111111',
)
gen1.set_password('test1234')
gen1.save()
log(f"Account 1: '{gen1.generator_name}'  login → password: test1234")

gen2 = Account(
    generator_name='مولدة الرصافة',
    phone='07702222222',
)
gen2.set_password('test1234')
gen2.save()
log(f"Account 2: '{gen2.generator_name}'  login → password: test1234")

# ── Subscribers ───────────────────────────────────────────────────────────────
print("\n[3/6] Creating subscribers...")

subscribers_data = [
    # (name, circuit, ambers, phone)
    ('أحمد علي محمد',    'A-01', 5,  '07710000001'),
    ('محمد حسن عبدالله', 'A-02', 3,  '07710000002'),
    ('علي كريم جاسم',    'A-03', 7,  '07710000003'),
    ('زهراء حسين عبيد',  'A-04', 5,  '07710000004'),
    ('عمر خالد رشيد',    'A-05', 10, '07710000005'),
    ('سارة محمود جابر',  'A-06', 5,  '07710000006'),
]

gen1_subs = []
for i, (name, circuit, ambers, phone) in enumerate(subscribers_data):
    s = Subscriber.objects.create(
        generator=gen1, name=name,
        circuit_number=circuit, ambers=ambers, phone=phone,
    )
    gen1_subs.append(s)
    log(f"  {circuit} — {name} ({ambers}A)")

gen2_subs = []
for i, (name, circuit, ambers, phone) in enumerate(subscribers_data):
    # Same names, different circuit prefix for gen2
    s = Subscriber.objects.create(
        generator=gen2, name=name,
        circuit_number=circuit.replace('A', 'B'), ambers=ambers,
        phone=phone[:-1] + str(int(phone[-1]) + 1),
    )
    gen2_subs.append(s)

log(f"Created {len(gen1_subs)} subscribers for each generator.")

# ── Workers ───────────────────────────────────────────────────────────────────
print("\n[4/6] Creating workers...")

w1 = Worker(generator=gen1, name='خالد محمد الجبوري', phone='07720000001')
w1.set_password('worker123')
w1.save()
log(f"Worker 1: '{w1.name}'  phone: {w1.phone}  pass: worker123")

w2 = Worker(generator=gen1, name='سامر علي السعيدي', phone='07720000002')
w2.set_password('worker123')
w2.save()
log(f"Worker 2: '{w2.name}'  phone: {w2.phone}  pass: worker123")

w3 = Worker(generator=gen2, name='حسن قاسم النجاشي', phone='07720000003')
w3.set_password('worker123')
w3.save()
log(f"Worker 3: '{w3.name}'  phone: {w3.phone}  pass: worker123")

# ── Budgets ───────────────────────────────────────────────────────────────────
print("\n[5/6] Creating monthly budgets...")

budgets_gen1 = []
for year, month, price in [(2026, 2, 12000), (2026, 3, 13500), (2026, 4, 15000)]:
    b = Budget.objects.create(generator=gen1, year=year, month=month, amber_price=price)
    budgets_gen1.append(b)
    log(f"  Gen1 budget: {year}/{month:02d} → {price:,} د.ع/أمبير")

budgets_gen2 = []
for year, month, price in [(2026, 2, 11000), (2026, 3, 12500), (2026, 4, 14000)]:
    b = Budget.objects.create(generator=gen2, year=year, month=month, amber_price=price)
    budgets_gen2.append(b)
    log(f"  Gen2 budget: {year}/{month:02d} → {price:,} د.ع/أمبير")

# ── Receipts ──────────────────────────────────────────────────────────────────
print("\n[6/6] Creating receipts...")

def make_receipts(generator, subscribers, budgets, worker):
    count = 0
    for budget in budgets:
        # Pay all but the last subscriber (so unpaid_count > 0)
        for sub in subscribers[:-1]:
            amount = float(budget.amber_price) * sub.ambers
            try:
                Receipt.objects.create(
                    generator=generator,
                    subscriber=sub,
                    worker=worker,
                    year=budget.year,
                    month=budget.month,
                    amber_price=budget.amber_price,
                    amount_paid=amount,
                    notes='تم الدفع نقداً',
                )
                count += 1
            except Exception:
                pass  # skip duplicates if re-run
    return count

r1 = make_receipts(gen1, gen1_subs, budgets_gen1, w1)
r2 = make_receipts(gen2, gen2_subs, budgets_gen2, w3)
log(f"Created {r1} receipts for Gen1, {r2} receipts for Gen2")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 52)
print("  ✅  Seed data created successfully!")
print("=" * 52)
print("""
LOGIN CREDENTIALS
─────────────────────────────────────────────────
Manager 1 : مولدة الكرخ       / test1234
Manager 2 : مولدة الرصافة     / test1234
Worker 1  : 07720000001       / worker123
Worker 2  : 07720000002       / worker123
─────────────────────────────────────────────────
Each generator has:
  • 6 subscribers  (5 paid, 1 unpaid per month)
  • 2–3 workers
  • 3 monthly budgets (Feb / Mar / Apr 2026)
  • Receipts with real amounts
""")

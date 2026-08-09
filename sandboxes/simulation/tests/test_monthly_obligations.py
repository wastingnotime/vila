import unittest

from app.simulation.monthly_obligations import run_monthly_obligations


class MonthlyObligationTests(unittest.TestCase):
    def test_unpaid_obligations_accumulate_manager_pressure(self) -> None:
        environment, overdue_counts = run_monthly_obligations()

        self.assertEqual(overdue_counts, [1, 2, 3])
        self.assertEqual(len(environment.payments), 9)
        self.assertEqual(sum(payment.status == "paid" for payment in environment.payments), 6)

    def test_payment_handoff_is_idempotence_guarded(self) -> None:
        environment, _ = run_monthly_obligations(months=1)

        with self.assertRaises(ValueError):
            environment.mark_payment_paid(0, environment.payments[0].paid_at)


if __name__ == "__main__":
    unittest.main()

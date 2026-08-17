"""Cross-user authorization. Real routes, real DB, two real users."""

from types import SimpleNamespace
from budget_app.testing import DatabaseTestCase
from ..extensions import db
from ..models import BudgetItem


class CrossUserAuthorizationTest(DatabaseTestCase):
    def setUp(self):
        super().setUp()

        self.victim = self.seed_user("victim", item_name="rent", item_total=123)

        self.attacker = self.seed_user("attacker", item_name="gas", item_total=67)

    def seed_user(
        self,
        username,
        item_name,
        item_total,
        gross_income=2345,
        month_duration=1,
        item_category="bills",
    ):
        """
        registers, logs in, creates a budget, creates an item,
        and returns namespace containing: client, budget_id, item_id
        """
        client = self.app.test_client()
        registered = client.post(
            "/api/auth/register",
            json={"username": username, "password": f"pw-{username}"},
        )
        self.assertEqual(200, registered.status_code, registered.get_json())

        login = client.post(
            "/api/auth/login", json={"username": username, "password": f"pw-{username}"}
        )
        self.assertEqual(200, login.status_code, login.get_json())

        budget = client.post(
            "/api/budget/create",
            json={
                "name": f"{username} budget",
                "gross_income": gross_income,
                "month_duration": month_duration,
            },
        )
        self.assertEqual(200, budget.status_code, budget.get_json())
        budget_id = budget.get_json()["budget"]["id"]

        item = client.post(
            "/api/budget/item/create",
            json={
                "name": item_name,
                "category": item_category,
                "total": item_total,
                "budget_id": budget_id,
            },
        )
        self.assertEqual(200, item.status_code, item.get_json())
        item_id = item.get_json()["budget_item_id"]

        return SimpleNamespace(client=client, budget_id=budget_id, item_id=item_id)

    def test_user_cannot_create_item_in_another_users_budget(self):
        # attacker POSTs /api/budget/item/create with the VICTIM's budget_id
        response = self.attacker.client.post(
            "/api/budget/item/create",
            json={
                "name": "attacker item",
                "category": "bills",
                "total": 9999,
                "budget_id": self.victim.budget_id,
            },
        )
        self.assertEqual(404, response.status_code)
        db.session.expire_all()

        attacker_item = BudgetItem.query.filter_by(
            budget_id=self.victim.budget_id, name="attacker item"
        ).first()
        self.assertIsNone(attacker_item)

    def test_user_cannot_edit_another_users_budget_item(self):
        response = self.attacker.client.post(
            "/api/budget/item/edit",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
                "name": "foo",
                "total": 9999,
            },
        )

        self.assertEqual(404, response.status_code)

        db.session.expire_all()
        item = db.session.get(BudgetItem, self.victim.item_id)
        self.assertEqual("rent", item.name)
        self.assertEqual(123.0, float(item.total))

    def test_user_cannot_delete_another_users_budget_item(self):
        response = self.attacker.client.post(
            "/api/budget/item/delete",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
            },
        )

        self.assertEqual(404, response.status_code)

        db.session.expire_all()
        self.assertIsNotNone(db.session.get(BudgetItem, self.victim.item_id))

    def test_user_can_edit_their_own_budget_item(self):
        response = self.victim.client.post(
            "/api/budget/item/edit",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
                "name": "foo",
                "total": 9999,
            },
        )

        self.assertEqual(200, response.status_code)

        db.session.expire_all()
        item = db.session.get(BudgetItem, self.victim.item_id)
        self.assertEqual("foo", item.name)
        self.assertEqual(9999, float(item.total))

    def test_user_can_delete_their_own_budget_item(self):
        response = self.victim.client.post(
            "/api/budget/item/delete",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
            },
        )

        self.assertEqual(200, response.status_code)

        db.session.expire_all()
        self.assertIsNone(db.session.get(BudgetItem, self.victim.item_id))

    def test_delete_response_does_not_echo_item_details(self):
        response = self.victim.client.post(
            "/api/budget/item/delete",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "Budget item has been deleted.", response.get_json()["message"]
        )
        self.assertNotIn("rent", response.get_data(as_text=True).lower())

    def test_unauthenticated_user_cannot_read_a_budget(self):
        response = self.client.get(f"/api/budget/{self.victim.budget_id}")

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "You must be authenticated to use this route.",
            response.get_json()["message"],
        )

    def test_unauthenticated_user_cannot_edit_budget_item(self):
        response = self.client.post(
            "/api/budget/item/edit",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
                "name": "foo",
            },
        )

        self.assertEqual(401, response.status_code)

        db.session.expire_all()
        item = db.session.get(BudgetItem, self.victim.item_id)
        self.assertEqual("rent", item.name)

    def test_unauthenticated_user_cannot_delete_budget_item(self):
        response = self.client.post(
            "/api/budget/item/delete",
            json={
                "item_id": self.victim.item_id,
                "budget_id": self.victim.budget_id,
            },
        )

        self.assertEqual(401, response.status_code)

        db.session.expire_all()
        self.assertIsNotNone(db.session.get(BudgetItem, self.victim.item_id))

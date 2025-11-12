from test._utils.domain_tester import DomainTester


def test_get_todo(app: DomainTester):
    with app.tester() as client:
        response = client.get("/features/todo")
        data = response.json
        assert response.status_code == 200
        assert data == "Hello from TodoController"

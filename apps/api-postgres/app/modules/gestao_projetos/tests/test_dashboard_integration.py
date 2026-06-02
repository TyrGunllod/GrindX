class TestDashboard:
    def test_carregar_dados_retorna_metrics(self, db_session):
        from app.modules.gestao_projetos.repositories.dashboard_repository import DashboardRepository
        from app.modules.gestao_projetos.services.dashboard_service import DashboardService
        repo = DashboardRepository(db_session)
        service = DashboardService(repo)
        result = service.carregar_dados()
        assert result.metrics.total_projetos == 0
        assert result.metrics.total_tarefas == 0
        assert result.progresso_projetos == []

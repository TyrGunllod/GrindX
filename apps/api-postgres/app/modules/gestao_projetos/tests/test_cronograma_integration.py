class TestCronograma:
    def test_listar_tarefas_gantt_vazio(self, db_session):
        from app.modules.gestao_projetos.repositories.cronograma_repository import CronogramaRepository
        from app.modules.gestao_projetos.services.cronograma_service import CronogramaService
        repo = CronogramaRepository(db_session)
        service = CronogramaService(repo)
        result = service.listar_tarefas_gantt()
        assert result.total == 0
        assert result.items == []

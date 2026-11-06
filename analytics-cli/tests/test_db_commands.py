from unittest.mock import Mock

from alembic.config import Config as AlembicConfig
from click.testing import CliRunner

from georchestra_analytics_cli import __main__ as main
from georchestra_analytics_cli.timescaledb import PolicySyncResult


class _Config:
    def get_logging_config_as_dict(self):
        return None


def _runner(monkeypatch):
    config = _Config()
    alembic_config = object()
    monkeypatch.setattr(main, "load_config_from", Mock(return_value=config))
    monkeypatch.setattr(main, "_get_alembic_config", Mock(return_value=alembic_config))
    return CliRunner(), alembic_config


def test_alembic_config_receives_loaded_cli_config(monkeypatch):
    config = _Config()
    monkeypatch.setattr(main, "conf", config)

    alembic_config = main._get_alembic_config()

    assert isinstance(alembic_config, AlembicConfig)
    assert alembic_config.attributes["app_config"] is config


def test_db_upgrade_defaults_to_head(monkeypatch):
    runner, config = _runner(monkeypatch)
    upgrade = Mock()
    monkeypatch.setattr(main.alembic_command, "upgrade", upgrade)

    result = runner.invoke(main.cli, ["db", "upgrade"])

    assert result.exit_code == 0, result.output
    upgrade.assert_called_once_with(config, "head")


def test_db_upgrade_accepts_explicit_revision(monkeypatch):
    runner, config = _runner(monkeypatch)
    upgrade = Mock()
    monkeypatch.setattr(main.alembic_command, "upgrade", upgrade)

    result = runner.invoke(main.cli, ["db", "upgrade", "--revision", "0001"])

    assert result.exit_code == 0, result.output
    upgrade.assert_called_once_with(config, "0001")


def test_db_stamp_defaults_to_baseline(monkeypatch):
    runner, config = _runner(monkeypatch)
    stamp = Mock()
    monkeypatch.setattr(main.alembic_command, "stamp", stamp)

    result = runner.invoke(main.cli, ["db", "stamp"])

    assert result.exit_code == 0, result.output
    stamp.assert_called_once_with(config, "0001")


def test_db_stamp_accepts_explicit_revision(monkeypatch):
    runner, config = _runner(monkeypatch)
    stamp = Mock()
    monkeypatch.setattr(main.alembic_command, "stamp", stamp)

    result = runner.invoke(main.cli, ["db", "stamp", "--revision", "base"])

    assert result.exit_code == 0, result.output
    stamp.assert_called_once_with(config, "base")


def test_db_current(monkeypatch):
    runner, config = _runner(monkeypatch)
    current = Mock()
    monkeypatch.setattr(main.alembic_command, "current", current)

    result = runner.invoke(main.cli, ["db", "current"])

    assert result.exit_code == 0, result.output
    current.assert_called_once_with(config, verbose=True)


def test_db_downgrade_defaults_to_previous_revision(monkeypatch):
    runner, config = _runner(monkeypatch)
    downgrade = Mock()
    monkeypatch.setattr(main.alembic_command, "downgrade", downgrade)

    result = runner.invoke(main.cli, ["db", "downgrade"])

    assert result.exit_code == 0, result.output
    downgrade.assert_called_once_with(config, "-1")


def test_db_sync_policies(monkeypatch):
    runner, _ = _runner(monkeypatch)
    sync = Mock(
        return_value=PolicySyncResult(
            chunk_interval="7 days", retention_action="unchanged"
        )
    )
    monkeypatch.setattr(main, "sync_timescaledb_policies", sync)

    result = runner.invoke(main.cli, ["db", "sync-policies"])

    assert result.exit_code == 0, result.output
    sync.assert_called_once_with(main.conf)
    assert "chunk_interval=7 days, retention=unchanged" in result.output


def test_aggregate_ogc_drains_queue(monkeypatch):
    runner, _ = _runner(monkeypatch)
    drain = Mock(return_value=4)
    monkeypatch.setattr(main, "_drain_ogc_queue", drain)

    result = runner.invoke(main.cli, ["aggregate-ogc", "--batch-size", "2"])

    assert result.exit_code == 0, result.output
    drain.assert_called_once_with(batch_size=2)
    assert "processed_buckets=4" in result.output


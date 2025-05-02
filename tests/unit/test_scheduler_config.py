import schedule

from bot.scheduler import bot_job, setup_schedule


class TestSchedulerConfig:
    @staticmethod
    def test_job_is_scheduled_correctly():
        # Given:
        schedule.clear()
        setup_schedule()

        # Then:
        jobs = list(schedule.jobs)

        assert len(jobs) == 17
        assert jobs[0].job_func.func == bot_job
        assert jobs[0].at_time.hour == 7
        assert jobs[-1].at_time.hour == 23

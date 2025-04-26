import schedule

import scheduler


class TestSchedulerConfig:
    @staticmethod
    def test_job_is_scheduled_correctly():
        # Given:
        schedule.clear()
        scheduler.setup_schedule()

        # Then:
        jobs = list(schedule.jobs)

        assert len(jobs) == 1
        assert jobs[0].job_func.func == scheduler.job
        assert jobs[0].at_time.minute == 30

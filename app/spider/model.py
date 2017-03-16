from app import db, Base


class Project(Base):
    __tablename__ = 'sk_project'

    project_name = db.Column(db.String(50))

    @classmethod
    def load_project(cls, project_list):
        for project in project_list:
            existed_project = cls.query.filter_by(project_name=project.project_name).first()
            if not existed_project:
                db.session.add(project)
                db.session.commit()

    @classmethod
    def find_project_by_id(cls, project_id):
        return Project.query.filter_by(id=project_id).first()

    def to_dict(self):
        return {
            "project_id": self.id,
            "project_name": self.project_name
        }


class SpiderInstance(Base):
    __tablename__ = 'sk_spider'

    spider_name = db.Column(db.String)
    project_id = db.Column(db.INTEGER, nullable=False, index=True)

    @classmethod
    def load_spider(cls, spider_model_list):
        for spider_model in spider_model_list:
            existed_spider_model = cls.query.filter_by(project_id=spider_model.project_id,
                                                       spider_name=spider_model.spider_name).first()
            if not existed_spider_model:
                db.session.add(spider_model)
                db.session.commit()

    @classmethod
    def list_spider_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    def to_dict(self):
        return dict(spider_instance_id=self.id,
                    spider_name=self.spider_name,
                    project_id=self.project_id)


class JobPriority():
    LOW, NORMAL, HIGH, HIGHEST = range(-1, 3)


class JobInstance(Base):
    __tablename__ = 'sk_job_instance'

    spider_name = db.Column(db.String(100), nullable=False, index=True)
    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    tags = db.Column(db.Text)  # job tag(split by , )
    spider_arguments = db.Column(db.Text)  # job execute arguments(split by , ex.: arg1=foo,arg2=bar)
    priority = db.Column(db.INTEGER)
    desc = db.Column(db.Text)
    cron_minutes = db.Column(db.String(20), default="0")
    cron_hour = db.Column(db.String(20), default="*")
    cron_day_of_month = db.Column(db.String(20), default="*")
    cron_day_of_week = db.Column(db.String(20), default="*")
    cron_month = db.Column(db.String(20), default="*")
    enabled = db.Column(db.INTEGER, default=0)  # 0/-1
    run_type = db.Column(db.String(20))  # periodic/onetime

    def to_dict(self):
        return dict(
            job_instance_id=self.id,
            spider_name=self.spider_name,
            tags=self.tags.split(',') if self.tags else None,
            spider_arguments=self.spider_arguments,
            priority=self.priority,
            desc=self.desc,
            cron_minutes=self.cron_minutes,
            cron_hour=self.cron_hour,
            cron_day_of_month=self.cron_day_of_month,
            cron_day_of_week=self.cron_day_of_week,
            cron_month=self.cron_month,
            enabled=self.enabled == 0,
            run_type=self.run_type

        )

    @classmethod
    def list_job_instance_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    @classmethod
    def find_job_instance_by_id(cls, job_instance_id):
        return cls.query.filter_by(id=job_instance_id).first()


class SpiderStatus():
    PENDING, RUNNING, FINISHED, CANCELED = range(4)


class JobExecution(Base):
    __tablename__ = 'sk_job_execution'

    project_id = db.Column(db.INTEGER, nullable=False, index=True)
    service_job_execution_id = db.Column(db.String(50), nullable=False, index=True)
    job_instance_id = db.Column(db.INTEGER, nullable=False, index=True)
    create_time = db.Column(db.DATETIME)
    start_time = db.Column(db.DATETIME)
    end_time = db.Column(db.DATETIME)
    running_status = db.Column(db.INTEGER, default=SpiderStatus.PENDING)
    running_on = db.Column(db.Text)

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'job_execution_id': self.id,
            'service_job_execution_id': self.service_job_execution_id,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'running_status': self.running_status,
            'running_on': self.running_on
        }

    @classmethod
    def find_job_execution_by_service_job_execution_id(cls, service_job_execution_id):
        return cls.query.filter_by(service_job_execution_id=service_job_execution_id).first()

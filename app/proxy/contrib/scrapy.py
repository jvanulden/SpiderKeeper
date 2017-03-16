import datetime

from app.proxy.spiderctrl import SpiderServiceProxy
from app.spider.model import SpiderStatus, Project, SpiderInstance
from app.util.http import request


class ScrapydProxy(SpiderServiceProxy):
    def __init__(self, host="localhost", port=6800):
        self.host = host
        self.port = port
        self.spider_status_name_dict = {
            SpiderStatus.PENDING: 'pending',
            SpiderStatus.RUNNING: 'running',
            SpiderStatus.FINISHED: 'finished'
        }
        super(ScrapydProxy, self).__init__("%s:%d" % (host, port))

    def _scrapyd_url(self):
        return "http://%s:%d" % (self.host, self.port)

    def get_project_list(self):
        data = request("get", self._scrapyd_url() + "/listprojects.json", return_type="json")
        result = []
        if data:
            for project_name in data['projects']:
                project = Project()
                project.project_name = project_name
                result.append(project)
        return result

    def get_spider_list(self, project_name):
        data = request("get", self._scrapyd_url() + "/listspiders.json?project=%s" % project_name,
                       return_type="json")
        result = []
        if data:
            for spider_name in data['spiders']:
                spider_instance = SpiderInstance()
                spider_instance.spider_name = spider_name
                result.append(spider_instance)
        return result

    def get_daemon_status(self):
        pass

    def get_job_list(self, project_name, spider_status):
        data = request("get", self._scrapyd_url() + "/listjobs.json?project=%s" % project_name,
                       return_type="json")
        result = []
        if data:
            for item in data[self.spider_status_name_dict[spider_status]]:
                start_time, end_time = None, None
                if item.get('start_time'):
                    start_time = datetime.datetime.strptime(item['start_time'], '%Y-%m-%d %H:%M:%S.%f')
                if item.get('end_time'):
                    end_time = datetime.datetime.strptime(item['end_time'], '%Y-%m-%d %H:%M:%S.%f')
                result.append(dict(id=item['id'], start_time=start_time, end_time=end_time))
        return result

    def start_spider(self, project_name, spider_name, arguments):
        post_data = dict(project=project_name, spider=spider_name)
        post_data.update(arguments)
        data = request("post", self._scrapyd_url() + "/schedule.json", data=post_data, return_type="json")
        return data['jobid'] if data else None

    def cancel_spider(self, project_name, job_id):
        post_data = dict(project=project_name, job=job_id)
        data = request("post", self._scrapyd_url() + "/schedule.json", data=post_data, return_type="json")
        return data != None

# -*- coding:utf-8 -*-
from datetime import datetime

from handlers.base.base_handler import BaseHandler
from models.tasks.tasks_publisher_accept_models import Tasks,CategoryTasks
from libs.tasks.tasks_lib import save_tasks_messages,save_category

class TaskPublishHanlder(BaseHandler):
    def get(self):
        task = Tasks()
        categorys = CategoryTasks.all()
        tasks_name = task.content
        user_name = self.get_current_user().name
        kw = {
            'tasks_name':tasks_name,
            'user_name':user_name,
            'categorys':categorys,
        }

        self.render('tasks/tasks_publisher.html',**kw)

    def post(self):
        content = self.get_argument('content',None)
        # category =self.get_argument('category',None)
        category_id = self.get_argument('category_id',None)

        print content,category_id
        current_user = self.get_current_user()

        print current_user
        result = save_tasks_messages(self,content,current_user,category_id)


        if result['status'] is True:
            return self.write({'status': 200, 'msg': result['msg']})
        else:
            return self.write({'status': 400, 'msg': result['msg']})

class CategoryManageHandler(BaseHandler):
    def get(self):
        return self.render('tasks/category_manage.html')

    def post(self):
        category_name = self.get_argument('category_content_task',None)
        print category_name
        result = save_category(self,category_name)

        if result['status'] is True:
            return self.write('分类添加成功')
        else:
            return self.write({'status': 400, 'msg': result['msg']})



class TasksAcceptHanlder(BaseHandler):
    '''
    展示任务列表
    '''
    def get(self):

        # current_uer = self.get_current_user()
        # tasks = Tasks.all()
        # print "+++++++"
        # print tasks
        categorys = CategoryTasks.all()
        category_id_str = self.get_argument('category_task')
        category_id = int(category_id_str)
        print category_id

        if category_id == 0:
            tasks = Tasks.all()
            print tasks


        else:
            tasks = CategoryTasks.by_id(category_id).tasks





        kw = {
            'tasks':tasks,
            'categorys':categorys,


        }
        self.render('tasks/tasks_accept.html',**kw)




class UserAcceptHandler(BaseHandler):
    '''
    点击接受任务
    '''
    def get(self):
        '''
        根据task id 取出任务
        :return:
        '''

        current_user = self.get_current_user()
        user_name = current_user.name
        task_id = self.get_argument('id','')

        task = Tasks.by_id(task_id)
        task_content = task.content
        print '******************'
        print task.content
        result_repeate = self.conn.sadd('tasks:mytasks%s'%user_name,task_id)

        print '+++++++++++='
        # print result
        if result_repeate:
            number_tasks = self.conn.smembers('tasks:mytasks%s'%user_name)
            # accepted_task = []
            # self.conn.expire('tasks:mytasks%s'%current_user,60*5)
            print number_tasks

            self.conn.set('tasks:%s%s' %(task_id,user_name), task_content)
            self.conn.set('tasks:%s%s' %(task_content,user_name), task_id)
            # self.conn.expire('tasks:%s' % task_id, 300)
            result_task_content_unexpire = self.conn.get('tasks:%s%s' %(task_id,user_name))
            if result_task_content_unexpire is None:
                return self.write('该任务已经被您取消或者过期，请获取其它的任务')
            # if task_id not in number_tasks:
            #     accepted_task.append(task_id)
            #     return self.write('该任务已经被您获取过，不能再次获取')
            # remain_task = 5 - len(number_tasks)
            # return self.write('您还要继续接%s个任务'%remain_task)

            # number_tasks = self.conn.smembers('tasks:mytasks%s' % user_name)
            # delete_task = self.conn.srem('tasks:mytasks%s'%user_name,task_id)



        else:
            return self.write('请不要重复的获取任务')

        # if tasks is not None:
        #     tasks_content = tasks.content
        # str_task_id = str(task_id)


        # self.conn.setex('tasks:%s'%user_name,tasks_content,2000)
        # self.write('成功接受任务')

class MyTasksHandler(BaseHandler):
    '''
    用户展示自己的任务
    '''
    def get(self):
        tasks_content = []
        current_user = self.get_current_user()
        user_name = current_user.name
        tasks_id = self.conn.smembers('tasks:mytasks%s'%user_name)

        for task_id in tasks_id:
            task_content = self.conn.get('tasks:%s%s'%(task_id,user_name))
            if task_content is not None:
                tasks_content.append(task_content)
            print '###############'
            print task_content
            # tasks_content.append(task_content)

        # print tasks_content
        current_user = self.get_current_user()
        user_id = self.get_argument('user_id','')
        # tasks = current_user.tasks
        # print '****************'
        # print tasks

        kw = {
            'current_user':current_user,
            'tasks':tasks_content,
            'num':0,
            'datetime':'5分钟',
            'tasks_id':tasks_id
        }
        return self.render('tasks/my_doing_tasks.html',**kw)


class QuitTaskHandler(BaseHandler):
    def get(self):
        current_user = self.get_current_user()
        user_name = current_user.name
        time_expire = 300
        task_content = self.get_argument('task_content','')
        task_id = self.conn.get('tasks:%s%s'%(task_content,user_name))

        # task_content = self.conn.get('tasks:%s'%task_id)
        # task_content = task.content
        # result = self.conn.srem('tasks:mytasks%s'%current_user, task_content)
        # if task_content is None:
        #     self.conn.sadd('Expire:tasks',task_id)
        #     return self.write('由于已经到了过期时间，从而失效')
        result_delete = self.conn.delete('tasks:%s%s'%(task_id,user_name))
        if result_delete:
            return self.write('您已经成功取消该任务')
# num = 0
class HaveDoneTasksHandler(BaseHandler):
    '''
    任务完成处理
    '''
    def get(self):
        current_user = self.get_current_user()
        current_user_name = current_user.name
        tasks_content = self.get_argument('task_content','')
        # print "***************"
        # print tasks_content
        task_id = self.conn.get('tasks:%s%s' %(tasks_content,current_user_name))
        # print task_id
        self.conn.expire('tasks:%s' % task_id, 300)
        # print task_id
        expire_content_task = self.conn.get('tasks:%s%s'%(task_id,current_user_name))

        # print expire_content_task
        if expire_content_task is not None:
            # self.conn.set('task_done:%s' % expire_content_task, num)
            result_num_done_task = self.conn.incr('task_done:%s'%expire_content_task)
            if result_num_done_task <= 5 and result_num_done_task > 0:
                task = Tasks.by_id(task_id)
                task.num_task = result_num_done_task
                self.db.add(task)
                self.db.commit()
                remain_task_done = 5 - result_num_done_task
                self.conn.delete('tasks:%s%s'%(task_id,current_user_name))

                return self.write('该任务已经完成了，还剩%s次'%remain_task_done)
            elif result_num_done_task > 5:
                return self.write('该任务已经被完成了5次，不能再次完成')
            #
            #
            #
            #
            # # num_task = str(NUM_TASK + 1)
            #
            # # self.conn.set('task_done:%s'%expire_content_task,num_task)
            # # num_done_tasks = self.conn.get('task_done:%s'%expire_content_task)
            # # print "***********"
            # # print num_done_tasks
            # task = Tasks.by_id(task_id)
            #
            # task.num_task += 1
            # # if task.num_task > 5:
            # #     return self.write('该任务已经被完成了5次了')
            # self.db.add(task)
            # self.db.commit()
            # self.conn.set('task_done:%s' % expire_content_task, task.num_task)
            # num_done_tasks = self.conn.get('task_done:%s' % expire_content_task)
            # print "***********"
            # print num_done_tasks
            # self.write('执行成功')
        else:
            return self.write('该任务已经过期或已经取消或者已经被您完成')


        # tasks_have_done_numbers = self.conn.smembers('tasks:havedone%s'%current_user_name)
        #
        # if len(tasks_have_done_numbers) < 5:
        #     remain_tasks_have_done = 5 - len(tasks_have_done_numbers)
        #     return self.write('您还有%s次任务需要完成'%remain_tasks_have_done)
        # elif len(tasks_have_done_numbers) == 5:
        #     return self.write('恭喜您，您已经完成了5次任务')


class CategoryTasksHandler(BaseHandler):
    def get(self):
        category = self.get_argument('category_content','')
        category_task_set = self.conn.smembers('tasks:%s'%category)
        kw = {
            'task_categorys':category_task_set,
            'category':category,
        }

        return self.render('tasks/category_tasks.html',**kw)

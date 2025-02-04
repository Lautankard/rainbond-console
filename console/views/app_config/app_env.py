# -*- coding: utf8 -*-
"""
  Created on 18/1/15.
"""
import logging

from django.db import connection
from django.forms.models import model_to_dict
from django.views.decorators.cache import never_cache
from rest_framework.response import Response
from console.services.app_config.env_service import AppEnvVarService
from console.utils.reqparse import parse_item
from console.utils.response import MessageResponse
from console.views.app_config.base import AppBaseView
from www.decorator import perm_required
from www.utils.return_message import error_message
from www.utils.return_message import general_message

logger = logging.getLogger("default")

env_var_service = AppEnvVarService()


class AppEnvView(AppBaseView):
    @never_cache
    @perm_required('view_service')
    def get(self, request, *args, **kwargs):
        """
        获取服务的环境变量参数
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: env_type
              description: 环境变量类型[对内环境变量（inner）|对外环境变量（outer）]
              required: true
              type: string
              paramType: query
        """
        try:
            env_type = request.GET.get("env_type", None)
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 10))
            env_name = request.GET.get("env_name", None)

            if not env_type:
                return Response(general_message(400, "param error", "参数异常"), status=400)
            if env_type not in ("inner", "outer"):
                return Response(general_message(400, "param error", "参数异常"), status=400)
            env_list = []
            if env_type == "inner":
                if env_name:
                    # 获取总数
                    cursor = connection.cursor()
                    cursor.execute("select count(*) from tenant_service_env_var where tenant_id='{0}' and \
                            service_id='{1}' and scope='inner' and attr_name like '%{2}%';".format(
                        self.service.tenant_id, self.service.service_id, env_name))
                    env_count = cursor.fetchall()

                    total = env_count[0][0]
                    start = (page - 1) * page_size
                    remaining_num = total - (page - 1) * page_size
                    end = page_size
                    if remaining_num < page_size:
                        end = remaining_num

                    cursor = connection.cursor()
                    cursor.execute("select ID, tenant_id, service_id, container_port, name, attr_name, \
                            attr_value, is_change, scope, create_time from tenant_service_env_var \
                                where tenant_id='{0}' and service_id='{1}' and scope='inner' and \
                                    attr_name like '%{2}%' order by attr_name LIMIT {3},{4};".format(
                        self.service.tenant_id, self.service.service_id, env_name, start, end))
                    env_tuples = cursor.fetchall()
                else:

                    cursor = connection.cursor()
                    cursor.execute("select count(*) from tenant_service_env_var where tenant_id='{0}' and service_id='{1}'\
                             and scope='inner';".format(self.service.tenant_id, self.service.service_id))
                    env_count = cursor.fetchall()

                    total = env_count[0][0]
                    start = (page - 1) * page_size
                    remaining_num = total - (page - 1) * page_size
                    end = page_size
                    if remaining_num < page_size:
                        end = remaining_num

                    cursor = connection.cursor()
                    cursor.execute("select ID, tenant_id, service_id, container_port, name, attr_name, attr_value,\
                             is_change, scope, create_time from tenant_service_env_var where tenant_id='{0}' \
                                 and service_id='{1}' and scope='inner' order by attr_name LIMIT {2},{3};".format(
                        self.service.tenant_id, self.service.service_id, start, end))
                    env_tuples = cursor.fetchall()
                if len(env_tuples) > 0:
                    for env_tuple in env_tuples:
                        env_dict = dict()
                        env_dict["ID"] = env_tuple[0]
                        env_dict["tenant_id"] = env_tuple[1]
                        env_dict["service_id"] = env_tuple[2]
                        env_dict["container_port"] = env_tuple[3]
                        env_dict["name"] = env_tuple[4]
                        env_dict["attr_name"] = env_tuple[5]
                        env_dict["attr_value"] = env_tuple[6]
                        env_dict["is_change"] = env_tuple[7]
                        env_dict["scope"] = env_tuple[8]
                        env_dict["create_time"] = env_tuple[9]
                        env_list.append(env_dict)
                bean = {"total": total}

            else:
                if env_name:

                    cursor = connection.cursor()
                    cursor.execute("select count(*) from tenant_service_env_var where tenant_id='{0}' and service_id='{1}'\
                             and scope='outer' and attr_name like '%{2}%';".format(self.service.tenant_id,
                                                                                   self.service.service_id, env_name))
                    env_count = cursor.fetchall()

                    total = env_count[0][0]
                    start = (page - 1) * page_size
                    remaining_num = total - (page - 1) * page_size
                    end = page_size
                    if remaining_num < page_size:
                        end = remaining_num

                    cursor = connection.cursor()
                    cursor.execute("select ID, tenant_id, service_id, container_port, name, attr_name, attr_value, is_change, \
                            scope, create_time from tenant_service_env_var where tenant_id='{0}' and service_id='{1}'\
                                 and scope='outer' and attr_name like '%{2}%' order by attr_name LIMIT {3},{4};".format(
                        self.service.tenant_id, self.service.service_id, env_name, start, end))
                    env_tuples = cursor.fetchall()
                else:

                    cursor = connection.cursor()
                    cursor.execute("select count(*) from tenant_service_env_var where tenant_id='{0}' and service_id='{1}' \
                            and scope='outer';".format(self.service.tenant_id, self.service.service_id))
                    env_count = cursor.fetchall()

                    total = env_count[0][0]
                    start = (page - 1) * page_size
                    remaining_num = total - (page - 1) * page_size
                    end = page_size
                    if remaining_num < page_size:
                        end = remaining_num

                    cursor = connection.cursor()
                    cursor.execute("select ID, tenant_id, service_id, container_port, name, attr_name, attr_value, is_change,\
                             scope, create_time from tenant_service_env_var where tenant_id='{0}' and service_id='{1}'\
                                  and scope='outer' order by attr_name LIMIT {2},{3};".format(
                        self.service.tenant_id, self.service.service_id, start, end))
                    env_tuples = cursor.fetchall()
                if len(env_tuples) > 0:
                    for env_tuple in env_tuples:
                        env_dict = dict()
                        env_dict["ID"] = env_tuple[0]
                        env_dict["tenant_id"] = env_tuple[1]
                        env_dict["service_id"] = env_tuple[2]
                        env_dict["container_port"] = env_tuple[3]
                        env_dict["name"] = env_tuple[4]
                        env_dict["attr_name"] = env_tuple[5]
                        env_dict["attr_value"] = env_tuple[6]
                        env_dict["is_change"] = env_tuple[7]
                        env_dict["scope"] = env_tuple[8]
                        env_dict["create_time"] = env_tuple[9]
                        env_list.append(env_dict)
                bean = {"total": total}

            result = general_message(200, "success", "查询成功", bean=bean, list=env_list)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    @never_cache
    @perm_required('manage_service_config')
    def post(self, request, *args, **kwargs):
        """
        为应用添加环境变量
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: name
              description: 环境变量说明
              required: false
              type: string
              paramType: form
            - name: attr_name
              description: 环境变量名称 大写
              required: true
              type: string
              paramType: form
            - name: attr_value
              description: 环境变量值
              required: true
              type: string
              paramType: form
            - name: scope
              description: 生效范围 inner(对内),outer(对外)
              required: true
              type: string
              paramType: form
            - name: is_change
              description: 是否可更改 (默认可更改)
              required: false
              type: string
              paramType: form

        """
        name = request.data.get("name", None)
        attr_name = request.data.get("attr_name", None)
        attr_value = request.data.get("attr_value", None)
        scope = request.data.get('scope', None)
        is_change = request.data.get('is_change', True)
        try:
            if not scope:
                return Response(general_message(400, "params error", "参数异常"), status=400)
            if scope not in ("inner", "outer"):
                return Response(general_message(400, "params error", "scope范围只能是inner或outer"), status=400)
            code, msg, data = env_var_service.add_service_env_var(self.tenant, self.service, 0, name, attr_name, attr_value,
                                                                  is_change, scope)
            if code != 200:
                result = general_message(code, "add env error", msg)
                return Response(result, status=code)
            result = general_message(code, msg, u"环境变量添加成功", bean=data.to_dict())
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class AppEnvManageView(AppBaseView):
    @never_cache
    @perm_required('manage_service_config')
    def delete(self, request, *args, **kwargs):
        """
        删除应用的某个环境变量
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: attr_name
              description: 环境变量名称 大写
              required: true
              type: string
              paramType: path

        """
        attr_name = kwargs.get("attr_name", None)
        if not attr_name:
            return Response(general_message(400, "attr_name not specify", u"环境变量名未指定"))
        try:
            env_var_service.delete_env_by_attr_name(self.tenant, self.service, attr_name)
            result = general_message(200, "success", u"删除成功")
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    @never_cache
    @perm_required('view_service')
    def get(self, request, *args, **kwargs):
        """
        获取应用的某个环境变量详情
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: attr_name
              description: 环境变量名称 大写
              required: true
              type: string
              paramType: path

        """
        attr_name = kwargs.get("attr_name", None)
        if not attr_name:
            return Response(general_message(400, "attr_name not specify", u"环境变量名未指定"))
        try:
            env = env_var_service.get_env_by_attr_name(self.tenant, self.service, attr_name)

            result = general_message(200, "success", u"查询成功", bean=model_to_dict(env))
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    @never_cache
    @perm_required('manage_service_config')
    def put(self, request, *args, **kwargs):
        """
        修改应用环境变量
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: attr_name
              description: 环境变量名称 大写
              required: true
              type: string
              paramType: path
             - name: name
              description: 环境变量说明
              required: false
              type: string
              paramType: form
            - name: attr_value
              description: 环境变量值
              required: true
              type: string
              paramType: form

        """
        attr_name = kwargs.get("attr_name", None)
        if not attr_name:
            return Response(general_message(400, "attr_name not specify", u"环境变量名未指定"))
        try:
            name = request.data.get("name", None)
            attr_value = request.data.get("attr_value", None)

            code, msg, env = env_var_service.update_env_by_attr_name(self.tenant, self.service, attr_name, name, attr_value)
            if code != 200:
                return Response(general_message(code, "update value error", msg))
            result = general_message(200, "success", u"查询成功", bean=model_to_dict(env))
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    @never_cache
    @perm_required('manage_service_config')
    def patch(self, request, attr_name, *args, **kwargs):
        """变更环境变量范围"""
        scope = parse_item(request, 'scope', required=True, error="scope is is a required parameter")
        env = env_var_service.patch_env_scope(self.tenant, self.service, attr_name, scope)
        return MessageResponse(msg="success", msg_show=u"更新成功", bean=env.to_dict())


class AppBuildEnvView(AppBaseView):
    @never_cache
    @perm_required('view_service')
    def get(self, request, *args, **kwargs):
        """
        获取构建服务的环境变量参数
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: serviceAlias
              description: 服务别名
              required: true
              type: string
              paramType: path
            - name: env_type
              description: 环境变量类型[构建运行时环境变量（build)]
              required: true
              type: string
              paramType: query
        """
        try:
            # 获取服务构建时环境变量
            build_env_dict = dict()
            build_envs = env_var_service.get_service_build_envs(self.service)
            if build_envs:
                for build_env in build_envs:
                    build_env_dict[build_env.attr_name] = build_env.attr_value
            result = general_message(200, "success", u"查询成功", bean=build_env_dict)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    def put(self, request, *args, **kwargs):
        """
        修改构建运行时环境变量
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            build_env_dict = request.data.get("build_env_dict", None)
            build_envs = env_var_service.get_service_build_envs(self.service)
            # 传入为空，清除
            if not build_env_dict:
                if not build_envs:
                    return Response(general_message(200, "success", u"设置成功"))
                for build_env in build_envs:
                    build_env.delete()
                    return Response(general_message(200, "success", u"设置成功"))

            # 传入有值，清空再添加
            if build_envs:
                for build_env in build_envs:
                    build_env.delete()
            for key, value in build_env_dict.items():
                name = "构建运行时环境变量"
                attr_name = key
                attr_value = value
                is_change = True
                code, msg, data = env_var_service.add_service_build_env_var(self.tenant, self.service, 0, name, attr_name,
                                                                            attr_value, is_change)
                if code != 200:
                    continue

            result = general_message(200, "success", u"环境变量添加成功")
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

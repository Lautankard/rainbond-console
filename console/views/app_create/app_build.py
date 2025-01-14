# -*- coding: utf8 -*-
"""
  Created on 18/2/1.
"""
import logging

from django.views.decorators.cache import never_cache
from rest_framework.response import Response

from console.repositories.deploy_repo import deploy_repo
from console.services.app import app_service
from console.services.app_actions import app_manage_service
from console.services.app_actions import event_service
from console.services.app_config import dependency_service
from console.services.app_config import env_var_service
from console.services.app_config import label_service
from console.services.app_config import port_service
from console.services.app_config import probe_service
from console.services.app_config import volume_service
from console.services.compose_service import compose_service
from console.views.app_config.base import AppBaseView
from console.views.base import RegionTenantHeaderView
from www.decorator import perm_required
from www.utils.return_message import error_message
from www.utils.return_message import general_message
from www.apiclient.baseclient import HttpClient

logger = logging.getLogger("default")


class AppBuild(AppBaseView):
    @never_cache
    @perm_required('deploy_service')
    def post(self, request, *args, **kwargs):
        """
        服务构建
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

        """
        probe = None
        is_deploy = request.data.get("is_deploy", True)
        status = 200
        try:
            if self.service.service_source == "third_party":
                is_deploy = False
                # 数据中心连接创建三方服务
                new_service = app_service.create_third_party_service(self.tenant, self.service, self.user.nick_name)
            else:
                # 数据中心创建应用
                new_service = app_service.create_region_service(self.tenant, self.service, self.user.nick_name)

            self.service = new_service
            # 为服务添加默认探针
            if self.is_need_to_add_default_probe():
                code, msg, probe = app_service.add_service_default_porbe(self.tenant, self.service)
                logger.debug("add default probe; code: {}; msg: {}".format(code, msg))
            if is_deploy:
                # 添加服务有无状态标签
                label_service.update_service_state_label(self.tenant, self.service)
                # 部署应用
                app_manage_service.deploy(self.tenant, self.service, self.user, group_version=None)

                # 添加应用部署关系
                deploy_repo.create_deploy_relation_by_service_id(service_id=self.service.service_id)

            result = general_message(200, "success", "构建成功")
            return Response(result, status=result["code"])
        except HttpClient.CallApiError as e:
            logger.exception(e)
            if e.status == 403:
                result = general_message(10407, "no cloud permission", e.message)
                status = e.status
            else:
                result = general_message(500, "call cloud api failure", e.message)
                status = 500
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
            status = 500
        # 删除probe
        # 删除region端数据
        if probe:
            probe_service.delete_service_probe(self.tenant, self.service, probe.probe_id)
        if self.service.service_source != "third_party":
            event_service.delete_service_events(self.service)
            port_service.delete_region_port(self.tenant, self.service)
            volume_service.delete_region_volumes(self.tenant, self.service)
            env_var_service.delete_region_env(self.tenant, self.service)
            dependency_service.delete_region_dependency(self.tenant, self.service)
            app_manage_service.delete_region_service(self.tenant, self.service)
        self.service.create_status = "checked"
        self.service.save()
        return Response(result, status=status)

    def is_need_to_add_default_probe(self):
        if self.service.service_source != "source_code":
            return True
        else:
            ports = port_service.get_service_ports(self.service)
            for p in ports:
                if p.container_port == 5000:
                    return False
            return True


class ComposeBuildView(RegionTenantHeaderView):
    @never_cache
    @perm_required('create_service')
    def post(self, request, *args, **kwargs):
        """
        docker-compose应用检测
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: group_id
              description: 组ID
              required: true
              type: string
              paramType: path
            - name: compose_id
              description: group_compose ID
              required: true
              type: string
              paramType: form
        """
        probe_map = dict()
        services = None

        try:
            compose_id = request.data.get("compose_id", None)
            if not compose_id:
                return Response(general_message(400, "params error", "参数异常"), status=400)
            group_compose = compose_service.get_group_compose_by_compose_id(compose_id)
            services = compose_service.get_compose_services(compose_id)
            # 数据中心创建应用
            new_app_list = []
            for service in services:
                new_service = app_service.create_region_service(self.tenant, service, self.user.nick_name)
                new_app_list.append(new_service)
                # 为服务添加默认探针
                code, msg, probe = app_service.add_service_default_porbe(self.tenant, new_service)
                if probe:
                    probe_map[service.service_id] = probe.probe_id
                # 添加服务有无状态标签
                label_service.update_service_state_label(self.tenant, new_service)

            group_compose.create_status = "complete"
            group_compose.save()
            for s in new_app_list:
                try:
                    app_manage_service.deploy(self.tenant, s, self.user, group_version=None)
                except Exception as e:
                    logger.exception(e)
                    continue

            result = general_message(200, "success", "构建成功")
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
            # 删除probe
            # 删除region端数据
            if services:
                for service in services:
                    if probe_map:
                        probe_id = probe_map.get(service.service_id)
                        probe_service.delete_service_probe(self.tenant, service, probe_id)

                    event_service.delete_service_events(service)
                    port_service.delete_region_port(self.tenant, service)
                    volume_service.delete_region_volumes(self.tenant, service)
                    env_var_service.delete_region_env(self.tenant, service)
                    dependency_service.delete_region_dependency(self.tenant, service)

                    app_manage_service.delete_region_service(self.tenant, service)
                    service.create_status = "checked"
                    service.save()

        return Response(result, status=result["code"])

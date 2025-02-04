# -*- coding: utf8 -*-
"""
  Created on 18/1/15.
"""
import logging

from django.views.decorators.cache import never_cache
from rest_framework.response import Response

from console.exception.main import AccountOverdueException
from console.exception.main import CallRegionAPIException
from console.exception.main import ResourceNotEnoughException
from console.exception.main import ServiceHandleException
from console.repositories.app import service_repo
from console.services.app import app_service
from console.services.app_actions import app_manage_service
from console.services.app_actions.app_deploy import AppDeployService
from console.services.app_actions.exception import ErrServiceSourceNotFound
from console.services.app_config import deploy_type_service
from console.services.app_config import volume_service
from console.services.app_config.env_service import AppEnvVarService
from console.services.market_app_service import market_app_service
from console.services.team_services import team_services
from console.views.app_config.base import AppBaseView
from console.views.base import RegionTenantHeaderView
from www.apiclient.regionapi import RegionInvokeApi
from www.decorator import perm_required
from www.utils.return_message import error_message
from www.utils.return_message import general_message

logger = logging.getLogger("default")

env_var_service = AppEnvVarService()
app_deploy_service = AppDeployService()
region_api = RegionInvokeApi()


class StartAppView(AppBaseView):
    @never_cache
    @perm_required('start_service')
    def post(self, request, *args, **kwargs):
        """
        启动服务
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
        try:
            new_add_memory = self.service.min_memory * self.service.min_node
            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, new_add_memory,
                                                           "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法启动"))
            code, msg = app_manage_service.start(self.tenant, self.service, self.user)
            bean = {}
            if code != 200:
                return Response(general_message(code, "start app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class StopAppView(AppBaseView):
    @never_cache
    @perm_required('stop_service')
    def post(self, request, *args, **kwargs):
        """
        停止服务
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
        try:
            code, msg = app_manage_service.stop(self.tenant, self.service, self.user)
            bean = {}
            if code != 200:
                return Response(general_message(code, "stop app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class ReStartAppView(AppBaseView):
    @never_cache
    @perm_required('restart_service')
    def post(self, request, *args, **kwargs):
        """
        重启服务
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
        try:
            code, msg = app_manage_service.restart(self.tenant, self.service, self.user)
            bean = {}
            if code != 200:
                return Response(general_message(code, "restart app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class DeployAppView(AppBaseView):
    @never_cache
    @perm_required('deploy_service')
    def post(self, request, *args, **kwargs):
        """
        部署服务
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
        try:
            group_version = request.data.get("group_version", None)
            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, 0, "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法部署"))
            code, msg, _ = app_deploy_service.deploy(self.tenant, self.service, self.user, version=group_version)
            bean = {}
            if code != 200:
                return Response(general_message(code, "deploy app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ErrServiceSourceNotFound as e:
            logger.exception(e)
            return Response(general_message(412, e.message, "无法找到云市应用的构建源"), status=412)
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class RollBackAppView(AppBaseView):
    @never_cache
    @perm_required('rollback_service')
    def post(self, request, *args, **kwargs):
        """
        回滚服务
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
            - name: deploy_version
              description: 回滚的版本
              required: true
              type: string
              paramType: form

        """
        try:
            deploy_version = request.data.get("deploy_version", None)
            upgrade_or_rollback = request.data.get("upgrade_or_rollback", None)
            if not deploy_version or not upgrade_or_rollback:
                return Response(general_message(400, "deploy version is not found", "请指明版本及操作类型"), status=400)

            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, 0, "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法操作"))
            code, msg = app_manage_service.roll_back(self.tenant, self.service, self.user, deploy_version,
                                                     upgrade_or_rollback)
            bean = {}
            if code != 200:
                return Response(general_message(code, "roll back app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class VerticalExtendAppView(AppBaseView):
    @never_cache
    @perm_required('manage_service_extend')
    def post(self, request, *args, **kwargs):
        """
        垂直升级服务
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
            - name: new_memory
              description: 内存大小(单位：M)
              required: true
              type: int
              paramType: form

        """
        try:
            new_memory = request.data.get("new_memory", None)
            if not new_memory:
                return Response(general_message(400, "memory is null", "请选择升级内存"), status=400)
            new_add_memory = (int(new_memory) * self.service.min_node) - self.service.min_node * self.service.min_memory
            if new_add_memory < 0:
                new_add_memory = 0
            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, new_add_memory,
                                                           "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法升级"))
            code, msg = app_manage_service.vertical_upgrade(self.tenant, self.service, self.user, int(new_memory))
            bean = {}
            if code != 200:
                return Response(general_message(code, "vertical upgrade error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class HorizontalExtendAppView(AppBaseView):
    @never_cache
    @perm_required('manage_service_extend')
    def post(self, request, *args, **kwargs):
        """
        水平升级服务
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
            - name: new_node
              description: 节点个数
              required: true
              type: int
              paramType: form

        """
        try:
            new_node = request.data.get("new_node", None)
            if not new_node:
                return Response(general_message(400, "node is null", "请选择节点个数"), status=400)
            new_add_memory = (int(new_node) - self.service.min_node) * self.service.min_memory
            if new_add_memory < 0:
                new_add_memory = 0
            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, new_add_memory,
                                                           "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法升级"))

            code, msg = app_manage_service.horizontal_upgrade(self.tenant, self.service, self.user, int(new_node))
            bean = {}
            if code != 200:
                return Response(general_message(code, "horizontal upgrade error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class BatchActionView(RegionTenantHeaderView):
    @never_cache
    @perm_required('stop_service')
    @perm_required('start_service')
    @perm_required('restart_service')
    @perm_required('manage_group')
    def post(self, request, *args, **kwargs):
        """
        批量操作服务
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: action
              description: 操作名称 stop| start|restart|delete|move
              required: true
              type: string
              paramType: form
            - name: service_ids
              description: 批量操作的服务ID 多个以英文逗号分隔
              required: true
              type: string
              paramType: form

        """
        try:
            action = request.data.get("action", None)
            service_ids = request.data.get("service_ids", None)
            move_group_id = request.data.get("move_group_id", None)
            if action not in ("stop", "start", "restart", "move"):
                return Response(general_message(400, "param error", "操作类型错误"), status=400)
            identitys = team_services.get_user_perm_identitys_in_permtenant(
                user_id=self.user.user_id, tenant_name=self.tenant_name)
            perm_tuple = team_services.get_user_perm_in_tenant(user_id=self.user.user_id, tenant_name=self.tenant_name)

            if action == "stop":
                if "stop_service" not in perm_tuple and "owner" not in identitys \
                        and "admin" not in identitys and "developer" not in identitys:
                    return Response(general_message(400, "Permission denied", "没有关闭应用权限"), status=400)
            if action == "start":
                if "start_service" not in perm_tuple and "owner" not in identitys and "admin" \
                        not in identitys and "developer" not in identitys:
                    return Response(general_message(400, "Permission denied", "没有启动应用权限"), status=400)
            if action == "restart":
                if "restart_service" not in perm_tuple and "owner" not in identitys and "admin" \
                        not in identitys and "developer" not in identitys:
                    return Response(general_message(400, "Permission denied", "没有重启应用权限"), status=400)
            if action == "move":
                if "manage_group" not in perm_tuple and "owner" not in identitys and "admin" \
                        not in identitys and "developer" not in identitys:
                    return Response(general_message(400, "Permission denied", "没有变更应用分组权限"), status=400)
            service_id_list = service_ids.split(",")
            code, msg = app_manage_service.batch_action(self.tenant, self.user, action, service_id_list, move_group_id)
            if code != 200:
                result = general_message(code, "batch manage error", msg)
            else:
                result = general_message(200, "success", "操作成功")
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class DeleteAppView(AppBaseView):
    @never_cache
    @perm_required('delete_service')
    def delete(self, request, *args, **kwargs):
        """
        删除服务
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
            - name: is_force
              description: true直接删除，false进入回收站
              required: true
              type: boolean
              paramType: form

        """
        try:
            is_force = request.data.get("is_force", False)

            code, msg = app_manage_service.delete(self.user, self.tenant, self.service, is_force)
            bean = {}
            if code != 200:
                return Response(general_message(code, "delete service error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class BatchDelete(RegionTenantHeaderView):
    @never_cache
    @perm_required('delete_service')
    def delete(self, request, *args, **kwargs):
        """
        批量删除应用
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: service_ids
              description: 批量操作的服务ID 多个以英文逗号分隔
              required: true
              type: string
              paramType: form
        """
        try:
            service_ids = request.data.get("service_ids", None)
            identitys = team_services.get_user_perm_identitys_in_permtenant(
                user_id=self.user.user_id, tenant_name=self.tenant_name)
            perm_tuple = team_services.get_user_perm_in_tenant(user_id=self.user.user_id, tenant_name=self.tenant_name)
            if "delete_service" not in perm_tuple and "owner" not in identitys and "admin" \
                    not in identitys and "developer" not in identitys:
                return Response(general_message(400, "Permission denied", "没有删除应用权限"), status=400)
            service_id_list = service_ids.split(",")
            services = service_repo.get_services_by_service_ids(service_id_list)
            msg_list = []
            for service in services:
                code, msg = app_manage_service.batch_delete(self.user, self.tenant, service, is_force=True)
                msg_dict = dict()
                msg_dict['status'] = code
                msg_dict['msg'] = msg
                msg_dict['service_id'] = service.service_id
                msg_dict['service_cname'] = service.service_cname
                msg_list.append(msg_dict)
            code = 200
            result = general_message(code, "success", "操作成功", list=msg_list)
            return Response(result, status=result['code'])
        except Exception as e:
            logger.exception(e)


class AgainDelete(RegionTenantHeaderView):
    @never_cache
    @perm_required('delete_service')
    def delete(self, request, *args, **kwargs):
        """
        二次确认删除应用
        ---
        parameters:
            - name: tenantName
              description: 租户名
              required: true
              type: string
              paramType: path
            - name: service_id
              description: 应用id
              required: true
              type: string
              paramType: form
        """
        try:
            service_id = request.data.get("service_id", None)
            identitys = team_services.get_user_perm_identitys_in_permtenant(
                user_id=self.user.user_id, tenant_name=self.tenant_name)
            perm_tuple = team_services.get_user_perm_in_tenant(user_id=self.user.user_id, tenant_name=self.tenant_name)
            if "delete_service" not in perm_tuple and "owner" not in identitys and "admin" \
                    not in identitys and "developer" not in identitys:
                return Response(general_message(400, "Permission denied", "没有删除应用权限"), status=400)
            service = service_repo.get_service_by_service_id(service_id)
            code, msg = app_manage_service.delete_again(self.user, self.tenant, service, is_force=True)
            bean = {}
            if code != 200:
                return Response(general_message(code, "delete service error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)

        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


class ChangeServiceTypeView(AppBaseView):
    @never_cache
    @perm_required('manage_service_extend')
    def put(self, request, *args, **kwargs):
        """
        修改服务的应用类型标签
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            extend_method = request.data.get("extend_method", None)
            if not extend_method:
                return Response(general_message(400, "select the application type", "请选择应用类型"), status=400)

            old_extend_method = self.service.extend_method
            # 状态从有到无，并且有本地存储的不可修改
            is_mnt_dir = 0
            tenant_service_volumes = volume_service.get_service_volumes(self.tenant, self.service)
            if tenant_service_volumes:
                for tenant_service_volume in tenant_service_volumes:
                    if tenant_service_volume.volume_type == "local":
                        is_mnt_dir = 1
            if old_extend_method != "stateless" and extend_method == "stateless" and is_mnt_dir:
                return Response(
                    general_message(400, "local storage cannot be modified to be stateless", "本地存储不可修改为无状态"), status=400)
            deploy_type_service.put_service_deploy_type(self.tenant, self.service, extend_method)
            result = general_message(200, "success", "操作成功")
        except CallRegionAPIException as e:
            result = general_message(e.code, "failure", e.message)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


# 更新服务组件
class UpgradeAppView(AppBaseView):
    @never_cache
    @perm_required('deploy_service')
    def post(self, request, *args, **kwargs):
        """
        更新
        """
        try:
            allow_create, tips = app_service.verify_source(self.tenant, self.service.service_region, 0, "start_app")
            if not allow_create:
                return Response(general_message(412, "resource is not enough", "资源不足，无法更新"))
            code, msg, _ = app_manage_service.upgrade(self.tenant, self.service, self.user)
            bean = {}
            if code != 200:
                return Response(general_message(code, "upgrade app error", msg, bean=bean), status=code)
            result = general_message(code, "success", "操作成功", bean=bean)
        except ServiceHandleException as e:
            raise e
        except ResourceNotEnoughException as re:
            raise re
        except AccountOverdueException as re:
            logger.exception(re)
            return Response(general_message(10410, "resource is not enough", re.message), status=412)
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


# 修改服务名称
class ChangeServiceNameView(AppBaseView):
    @never_cache
    @perm_required('manage_service_extend')
    def put(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            service_name = request.data.get("service_name", None)
            if not service_name:
                return Response(general_message(400, "select the application type", "请输入修改后的名称"), status=400)
            extend_method = self.service.extend_method
            if extend_method == "stateless":
                return Response(general_message(400, "stateless applications cannot be modified", "无状态应用不可修改"), status=400)
            self.service.service_name = service_name
            self.service.save()
            result = general_message(200, "success", "操作成功")
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


# 修改服务名称
class ChangeServiceUpgradeView(AppBaseView):
    @never_cache
    @perm_required('manage_service_extend')
    def put(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            build_upgrade = request.data.get("build_upgrade", True)

            self.service.build_upgrade = build_upgrade
            self.service.save()
            result = general_message(200, "success", "操作成功", bean={"build_upgrade": self.service.build_upgrade})
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])


# 判断云市安装的应用是否有（小版本，大版本）更新
class MarketServiceUpgradeView(AppBaseView):
    @never_cache
    @perm_required('deploy_service')
    def get(self, request, *args, **kwargs):
        if self.service.service_source != "market":
            return Response(
                general_message(400, "non-cloud installed applications require no judgment", "非云市安装的应用无需判断"), status=400)

        # 判断服务状态，未部署的服务不提供升级数据
        try:
            body = region_api.check_service_status(self.service.service_region, self.tenant.tenant_name,
                                                   self.service.service_alias, self.tenant.enterprise_id)
            status = body["bean"]["cur_status"]
        except Exception as e:
            logger.exception(e)
            status = "unknown"
        if status == "undeploy" or status == "unknown":
            result = general_message(200, "success", "查询成功", list=[])
            return Response(result, status=result["code"])

        # List the versions that can be upgraded
        versions = market_app_service.list_upgradeable_versions(self.tenant, self.service)
        if versions is None:
            versions = []
        return Response(status=200, data=general_message(200, "success", "查询成功", list=versions))

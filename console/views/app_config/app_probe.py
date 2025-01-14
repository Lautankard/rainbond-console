# -*- coding: utf8 -*-
"""
  Created on 18/1/15.
"""
import logging

from django.views.decorators.cache import never_cache
from rest_framework.response import Response

from console.exception.main import AbortRequest
from console.serializer import ProbeSerilizer
from console.services.app_config import probe_service
from console.views.app_config.base import AppBaseView
from www.apiclient.regionapibaseclient import RegionApiBaseHttpClient
from www.decorator import perm_required
from www.utils.return_message import error_message
from www.utils.return_message import general_message

logger = logging.getLogger("default")


class AppProbeView(AppBaseView):
    @never_cache
    def get(self, request, *args, **kwargs):
        """
        获取服务指定模式的探针
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
            - name: mode
              description: 不健康处理方式（readiness|liveness|ignore）
              required: true
              type: string
              paramType: query
        """
        try:
            if self.service.service_source == "third_party":
                code, msg, probe = probe_service.get_service_probe(self.service)
                if code != 200:
                    return Response(general_message(code, "get probe error", msg))
                result = general_message(200, "success", "查询成功", bean=probe.to_dict())
            else:
                mode = request.GET.get("mode", None)
                if not mode:
                    code, msg, probe = probe_service.get_service_probe(self.service)
                    if code != 200:
                        return Response(general_message(code, "get probe error", msg))
                    result = general_message(200, "success", "查询成功", bean=probe.to_dict())
                else:
                    code, msg, probe = probe_service.get_service_probe_by_mode(self.service, mode)
                    if code != 200:
                        return Response(general_message(code, "get probe error", msg))
                    if not mode:
                        result = general_message(200, "success", "查询成功", list=probe)
                    else:
                        result = general_message(200, "success", "查询成功", bean=probe.to_dict())
            return Response(result, status=result["code"])
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
            return Response(result, status=result["code"])

    @never_cache
    @perm_required('manage_service_config')
    def post(self, request, *args, **kwargs):
        """
        添加服务探针
        ---
        serializer: ProbeSerilizer
        """
        try:
            data = request.data

            serializer = ProbeSerilizer(data=data)
            if not serializer.is_valid():
                result = general_message(400, "{0}".format(serializer.errors), "参数异常")
                return Response(result, status=result["code"])
            params = dict(serializer.data)
            code, msg, probe = probe_service.add_service_probe(self.tenant, self.service, params)
            if code != 200:
                return Response(general_message(code, "add probe error", msg))
            result = general_message(200, u"success", "添加成功", bean=probe.to_dict())
        except Exception as e:
            logger.exception(e)
            result = error_message(e.message)
        return Response(result, status=result["code"])

    @never_cache
    @perm_required('manage_service_config')
    def put(self, request, *args, **kwargs):
        """
        修改服务探针,包括启用停用 mode参数必填
        ---
        serializer: ProbeSerilizer
        """
        data = request.data

        try:
            code, msg, probe = probe_service.update_service_probea(tenant=self.tenant, service=self.service, data=data)
        except RegionApiBaseHttpClient.CallApiError as e:
            logger.exception(e)
            raise AbortRequest(msg=e.message, status_code=e.status)
        if code != 200:
            return Response(general_message(code, "update probe error", msg), status=code)
        result = general_message(200, u"success", "修改成功", bean=probe.to_dict())
        return Response(result, status=result["code"])

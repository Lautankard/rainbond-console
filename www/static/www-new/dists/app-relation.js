webpackJsonp([10],{24:function(module,exports,__webpack_require__){"use strict";function _interopRequireDefault(obj){return obj&&obj.__esModule?obj:{default:obj}}Object.defineProperty(exports,"__esModule",{value:!0});var _pageController=__webpack_require__(2),_pageController2=_interopRequireDefault(_pageController),_appApiCenter=__webpack_require__(1),_pageAppApiCenter=__webpack_require__(3),_widget=__webpack_require__(0),_widget2=_interopRequireDefault(_widget),Msg=_widget2.default.Message,template=__webpack_require__(39),AppRelation=(0,_pageController2.default)({template:template,property:{tenantName:"",serviceAlias:"",renderData:{appInfo:{},pageData:{}}},method:{getInitData:function(){var _this=this;(0,_appApiCenter.getAppInfo)(this.tenantName,this.serviceAlias).done(function(appInfo){_this.renderData.appInfo=appInfo,(0,_pageAppApiCenter.getPageRelationAppData)(_this.tenantName,_this.serviceAlias).done(function(pageData){_this.renderData.pageData=pageData,_this.render(),setTimeout(function(){_this.checkIsEnhanced(),$(".fn-tips").tooltip()})})})},checkIsEnhanced:function(){(0,_appApiCenter.isAppEnhanced)(this.tenantName,this.serviceAlias).done(function(data){!0===data?($(".fn-high-relation").show(),$(".openHightraly").hide(),$(".closeHightraly").show()):($(".fn-high-relation").hide(),$(".openHightraly").show(),$(".closeHightraly").hide())}).fail(function(){$(".fn-high-relation").hide()})},handleCreateAppRelation:function(destServiceAlias){var self=this;(0,_appApiCenter.createAppRelation)(this.tenantName,this.serviceAlias,destServiceAlias).done(function(){Msg.success("操作成功"),self.getInitData()})},handleCancelAppRelation:function(destServiceAlias){var self=this;(0,_appApiCenter.cancelAppRelation)(this.tenantName,this.serviceAlias,destServiceAlias).done(function(){Msg.success("操作成功"),self.getInitData()})},handleSettingAppRelation:function(depServiceName){var tenantName=this.tenantName,curServiceName=this.serviceAlias;$.ajax({type:"GET",url:"/ajax/"+tenantName+"/"+curServiceName+"/l7info",data:{dep_service_id:depServiceName},cache:!1,async:!1,beforeSend:function(xhr,settings){var csrftoken=$.cookie("csrftoken");xhr.setRequestHeader("X-CSRFToken",csrftoken)},success:function(data){function submit(){var obox={},oneonoff=$("#domainurl").prop("checked"),domainval=$("#dourl").val(),cricuitval=$("#fusing option:selected").attr("value");if(oneonoff&&!domainval)return Msg.warning("请填写domain"),!1;1==oneonoff&&(obox.domain=domainval),obox.cricuit=cricuitval;var oboxstr=JSON.stringify(obox);$.ajax({type:"POST",url:"/ajax/"+tenantName+"/"+curServiceName+"/l7info",data:{dep_service_id:depServiceName,l7_json:oboxstr},cache:!1,async:!1,beforeSend:function(xhr,settings){var csrftoken=$.cookie("csrftoken");xhr.setRequestHeader("X-CSRFToken",csrftoken)},success:function(data){"success"==data.status?(Msg.success("设置成功！"),dialog.destroy()):Msg.warning("设置失败！")},error:function(){Msg.danger("系统异常")}})}var servenlayer=data,domainUrl=servenlayer.domain,hasDoMainUrl="close"!=domainUrl&&"off"!=domainUrl,oStrH='<form class="form-horizontal"><div class="form-group"><span class="col-sm-2 control-label">转发</span><div class="col-sm-8"><input type="checkbox" name="domainurl"  id="domainurl" '+(hasDoMainUrl?'checked="checked"':"")+'  class="checkhide" /></div></div><div class="domain-form-group form-group" '+(hasDoMainUrl?"":'style="display:none"')+'><span class="col-sm-2 control-label">domain</span><div class="col-sm-8"><input class="form-control" type="text" value="'+(hasDoMainUrl?domainUrl:"")+'" id="dourl"/></div></div><div class="form-group"><span class="col-sm-2 control-label">熔断</span><div class="col-sm-8"><select class="form-control" id="fusing"><option value="0">0</option><option value="128">128</option><option value="256">256</option><option value="512">512</option><option value="1024">1024</option></select><span class="help-block">说明：熔断器数值表示同一时刻最大所允许向下游访问的最大连接数，设置为0时则完全熔断。</span></div></div></form>',cricuit=servenlayer.cricuit,dialog=_widget2.default.create("dialog",{title:"设置",domEvents:{".btn-success click":function(){submit()}}});dialog.setContent(oStrH),$("#fusing option").each(function(){var othis=$(this);$(this).attr("value")==cricuit&&$(othis).attr("selected",!0)}),$("#domainurl").change(function(){1==$("#domainurl").prop("checked")?$(".domain-form-group").show():$(".domain-form-group").hide()})},error:function(){Msg.danger("系统异常")}})},handleViewConnectInfo:function(tmp){_widget2.default.create("dialog",{title:"连接信息",content:tmp,height:"400px",autoDestroy:!0,btns:[{classes:"btn btn-default btn-cancel",text:"关闭"}]})},handleOpenAppSuper:function(){var self=this;(0,_appApiCenter.openAppSuper)(this.tenantName,this.serviceAlias).done(function(data){self.getInitData()}).fail(function(data){$("[name=hightraly]").prop("checked",!1)})},handleCloseAppSuper:function(){var self=this;(0,_appApiCenter.closeAppSuper)(this.tenantName,this.serviceAlias).done(function(data){self.getInitData()}).fail(function(data){$("[name=hightraly]").prop("checked",!0)})}},domEvents:{".createAppRelation click":function(e){var destServiceAlias=$(e.currentTarget).parents("tr").attr("data-dest-service-alias");destServiceAlias&&this.handleCreateAppRelation(destServiceAlias)},".cancelAppRelation click":function(e){var destServiceAlias=$(e.currentTarget).parents("tr").attr("data-dest-service-alias");destServiceAlias&&this.handleCancelAppRelation(destServiceAlias)},".setting-app-relation click":function(e){var destServiceAlias=$(e.currentTarget).parents("tr").attr("data-dest-service-alias");destServiceAlias&&this.handleSettingAppRelation(destServiceAlias)},".viewConnectInfo click":function(e){var $target=$(e.currentTarget),tmp=$target.closest("tr").find(".connectInfoTmp");this.handleViewConnectInfo(tmp.html())},".openHightraly click":function(e){this.handleOpenAppSuper()},".closeHightraly click":function(e){this.handleCloseAppSuper()}},onReady:function(){this.renderData.tenantName=this.tenantName,this.renderData.serviceAlias=this.serviceAlias,this.getInitData()}});window.AppRelationController=AppRelation,exports.default=AppRelation},39:function(module,exports){module.exports='{{if pageData.actions[\'manage_service\']}}\n{{ set curServiceEnvVarList = pageData.currentEnvMap[appInfo.service.service_id]}}\n  \n  <section class="panel panel-default">\n      <div class="panel-heading">连接信息</div>\n      <div class="panel-body">\n          <table class="table">\n            <thead>\n                <tr class="active tooltipTr">\n                  <th>\n                    <div data-toggle="tooltip" data-placement="top" title="其他应用依赖当前应用时，所需要的连接信息。" class="fn-tips">\n                      说明\n                    </div>\n                  </th>\n                  <th>\n                    <div data-toggle="tooltip" data-placement="top" title="指明依赖当前应用的其他应用，在编码中可以使用变量名来连接当前应用。" class="fn-tips">\n                       变量名\n                    </div>\n                  </th>\n                  <th>\n                    <div data-toggle="tooltip" data-placement="top" title="指明依赖当前应用的其他应用，在编码中可以使用变量值来连接当前应用。某些变量值也用于用户通过外部网络访问当前应用。" class="fn-tips">\n                      变量值\n                    </div>\n                  </th>\n                </tr>\n            </thead>\n            <tbody>\n            {{each curServiceEnvVarList || []}}\n                {{if $value.name != ""}}\n                    {{if (pageData.containerPortList.indexOf($value.container_port) >=0) || ($value.container_port < 1)}}\n                        <tr>\n                            <td>{{$value.name}}</td>\n                            <td>{{$value.attr_name}}</td>\n                            <td>{{$value.attr_value}}</td>\n                        </tr>\n                    {{/if}}\n                {{/if}}\n            {{/each}}\n            </tbody>\n          </table>\n      </div>\n  </section>\n{{/if}}\n\n\n{{if !pageData.is_private &&  pageData.cloud_assistant == \'goodrain\' }}\n    {{if appInfo.service.service_key == \'0000\' || appInfo.service.category == "app_publish"}}\n    <section class="panel panel-default" style="display: none;">\n        <div class="panel-heading">应用特性增强</div>\n        <div class="panel-body">\n          <p class="onoffbox clearfix">\n          <button style="display: none;" class="btn btn-success  btn-sm openHightraly pull-right">开启</button>\n          <button style="display: none;" class="btn btn-danger  btn-sm closeHightraly pull-right">关闭</button>\n          <span style="color: #838383; line-height: 30px; padding-left: 10px; font-size: 12px;">打开此开关则启动反向代理、负载均衡、熔断器等功能。熔断阀值需在依赖中对应的应用里设置。</span></p>\n        </div>\n    </section>\n   {{/if}}\n{{/if}}\n \n\n {{if appInfo.service.category == "application" || appInfo.service.category == "manager" || appInfo.service.category == "app_publish" || appInfo.service.category == "app_sys_publish" }}\n <section class="panel panel-default">\n      <div class="panel-heading">应用连接<small>(指定依赖其他应用后需重启)</small></div>\n      <div class="panel-body">\n          <table class="table">\n              <thead>\n              <tr class="active">\n                  <th>应用类型</th>\n                  <th>应用名称</th>\n                  <th>操作</th>\n              </tr>\n              </thead>\n              <tbody>\n              {{ if pageData.serviceIds }}\n                  {{each pageData.serviceIds}}\n                      {{if pageData.serviceMap[$value] && pageData.envMap[$value]}}\n                      <tr  data-dest-service-alias="{{pageData.serviceMap[$value].service_alias}}">\n                          <td>{{pageData.serviceMap[$value].service_type}}</td>\n                          <td>{{pageData.serviceMap[$value].service_cname}}</td>\n                          <td class="text-right">\n                              <div class="pull-right">\n                                {{if pageData.actions[\'manage_service\']}}\n                                <button type="button" class="btn btn-default btn-sm cancelAppRelation">取消</button>\n                                {{/if}}\n                                {{if pageData.actions[\'manage_service\'] || pageData.is_sys_admin}}\n                                <button class="btn btn-default btn-sm viewConnectInfo">连接信息</button>\n                                <script type="text/template" class="connectInfoTmp">\n                                  <table class="table">\n                                    <thead>\n                                      <tr class="active">\n                                        <th>说明</th>\n                                        <th>变量名</th>\n                                        <th>变量值</th>\n                                      </tr>\n                                    </thead>\n                                    <tbody>\n                                     {{each pageData.envMap[$value] $curServiceEnvVar $index}}\n                                     <tr>\n                                       <td>{{$curServiceEnvVar.name}}</td>\n                                       <td>{{$curServiceEnvVar.attr_name}}</td>\n                                       <td>{{$curServiceEnvVar.attr_value}}</td>\n                                     </tr>\n                                     {{/each}}\n                                    </tbody>\n                                  </table>\n                                <\/script>\n                                {{/if}}\n                                <a class="btn btn-success btn-sm fn-high-relation setting-app-relation"  style="color: #fff;display: none;" href="javascript:void(0)">设置</a>\n                            </div>\n                          </td>\n                      </tr>\n                      {{/if}}\n                  {{/each}}\n              {{/if}}\n\n              {{if pageData.serviceMap}}\n                {{if pageData.actions[\'manage_service\'] || pageData.is_sys_admin}}\n                    {{each pageData.serviceMap $value $key}}\n                        {{if (pageData.serviceIds || []).indexOf($key) < 0}}\n                           <tr data-dest-service-alias="{{$value.service_alias}}">\n                                <td>{{$value.service_type}}</td>\n                                <td>{{$value.service_cname}}</td>\n                                <td class="text-right">\n                                    <button type="button" class="btn btn-success btn-sm createAppRelation">关联</button>\n                                </td>\n                            </tr>\n                        {{/if}}\n                    {{/each}}\n                {{/if}}\n              {{/if}}\n             </tbody>\n          </table>\n      </div>\n  </section>\n{{/if}}'},74:function(module,exports,__webpack_require__){module.exports=__webpack_require__(24)}},[74]);
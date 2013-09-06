//task.js

var taskJS = function(){
	var self = this;
	var task_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var task_store = new Object();		//定义全局store，方便其他方法中的调用
	
	this.ext_task = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");

		self.task_store = new Ext.data.JsonStore({
			url : '/task/' + param,
			root : 'data',
			//totalProperty : 'total_count',
			//remoteSort : true,
			//pruneModifiedRecords: true, 
			fields : [
				{name: 'hash', type: 'string'},
				'create_time',
				'hits_num',
				'cold'
			]
		});

		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var task_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'hash', id : 'hash', dataIndex : 'hash', sortable : true},
			{header : 'create_time', id : 'create_time', dataIndex : 'create_time', sortable : true, },
			{header : 'hits_num', id : 'hits_num', dataIndex : 'hits_num', sortable : true},
			{header : 'cold', id : 'cold', dataIndex : 'cold', sortable : true},			
		]);

		self.task_store.load();
		self.task_grid = new Ext.grid.EditorGridPanel({
			id : tab_id,
			title : tab_title,
			iconCls : 'tabs',
			closable : true,
			columnLines : true,		//True表示为在列分隔处显示分隔符
			collapsible : false,		//面板是否可收缩的
			stripeRows : true,		//隔行变色
			store : self.task_store,
			colModel : task_mode,
			selModel : sel_mode,
			loadMask : {msg:'正在加载数据，请稍侯……'},
			//stateId : tab_id+'_grid'
			viewConfig : {
				forceFit:true,sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'//列按比率分配，占满整个grid
			},
			tbar : [{
				text:'刷新',
				iconCls : 'refresh',
				handler : self.refresh_task
			}/*,'-',{
				id: 'add_task_button',
				text: '新增',
				//hidden: true,
				iconCls: 'add',
				handler: self.addTaskBegin
			},'-',{
				id: 'reset_button',
				text: '重置所有',
				//hidden: true,
				iconCls: 'reset',
				handler: self.reset_task
			},'-',{
				id: 'delete_button',
				text: '删除所有',
				//hidden: true,
				iconCls: 'delete',
				handler: self.delete_task
			}*/]/*,'-',{
				text:'下载报表',
				tooltip:"下载报表",
				width:75,xtype:'button',
				iconCls:'down',
				//handler:self.down_ms_csv
			},'->',{
				id: 'pc_task_global_info',
				text:'',
				xtype:'tbtext'
			}]*/
		});
		main_panel.add(self.task_grid);
		main_panel.setActiveTab(self.task_grid);
		
		function task_status(value) {
			switch(value) {
				case 0: return '初始状态'; break;
				case 1: return '添加成功'; break;
				case 2: return '<span class="green">正在转码</span>'; break;
				case 3: return '转码成功'; break;
				case 4: return '<span class="red">转码失败</span>'; break;
				case 5: return '等待打包'; break;
				case 6: return '<span class="green">正在打包</span>'; break;
				case 7: return '打包成功'; break;
				case 8: return '<span class="red">打包失败</span>'; break;
				case 9: return '等待删除'; break;
				case 10: return '<span class="green">正在删除</span>'; break;
				case 11: return '删除成功'; break;
				case 12: return '<span class="red">删除失败</span>'; break;
				default:
					return '<span class="grey">未知状态</span>';
			}
		}

		function notify_status(value) {
			switch(value) {
				case 100: return '未通知'; break;
				case 101: return '<span class="green">转码结果通知中</span>'; break;
				case 102: return '转码结果通知成功'; break;
				case 103: return '<span class="red">转码结果通知失败</span>'; break;
				case 104: return '<span class="green">打包结果通知中</span>'; break;
				case 105: return '打包结果通知成功'; break;
				case 106: return '<span class="red">打包结果通知失败</span>'; break;
				default:
					return '<span class="grey">未知状态</span>';
			}
		}

		function delete_status(value) {
			switch(value) {
				case 0: return '未删除'; break;
				case 1: return '等待删除'; break;
				case 2: return '<span class="green">删除中</span>'; break;
				case 3: return '删除成功'; break;
				case 4: return '<span class="red">删除失败</span>'; break;
				default:
					return '<span class="grey">未知状态</span>';
			}
		}

		function task_type(value) {
			switch(value) {
				case 0: return '普通任务'; break;
				case 1: return '爬虫任务'; break;
				default:
					return '<span class="grey">未知任务</span>';
			}
		}

		function task_preview(value) {
			return '<a href="' + value + '" target="_blank">' + value +  '</a>';
		}
	};

	/**
	 * 刷新列表
	 */
	this.refresh_task = function() {
		self.task_store.reload();
	}

	this.reset_task = function() {
		Ext.Ajax.request({
			url: "/reset_task/",
			success: function(response) {
				Ext.MessageBox.alert('成功', Ext.encode(response));
				self.task_store.reload();
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});
	}

	this.delete_task = function() {
		Ext.Ajax.request({
			url: "/delete_task/",
			success: function(response) {
				Ext.MessageBox.alert('成功', Ext.encode(response));
				self.task_store.reload();
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});
	}
	
	/**
	 * 添加转码任务
	 */
	this.addTaskBegin = function() {
		if (Ext.get("add_task_info_win")) {
			Ext.getCmp("add_task_info_win").show();
			return;	//同时只存在一个添加权限信息的页面
		}
		
		var add_task_form = new Ext.FormPanel({
			id: 'add_task_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [
				{fieldLabel:'任务类型', name:'task_type'},
				{fieldLabel:'转码结果通知url', name:'notify_url'},
				{fieldLabel:'优先级', id:'priority', xtype:'numberfield'},
				{fieldLabel:'源地址', id:'source_url'},
			],
			buttons: [{
				text: '增加',
				handler: self.addTaskEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("add_task_info_win").close();}
			}]
		});
		
		var win = new Ext.Window({
			width:600,height:500,minWidth:400,minHeight:200,
			autoScroll:'auto',
			title : "新增转码任务",
			id : "add_task_info_win",
			renderTo: "ext_task",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: add_task_form
		}).show();
	};
	
	this.addTaskEnd = function() {
		Ext.getCmp('add_task_form').form.submit({
			waitMsg : '正在添加......',
			url : '/add_task/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("add_task_info_win").close();
				Ext.MessageBox.alert('成功', result.data.message);
				self.task_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
			},
			failure : function(form, action) {
				if (typeof(action.response) == 'undefined') {
					Ext.MessageBox.alert('警告','添加失败，请重新添加！');
				} else {
					var result = Ext.util.JSON.decode(action.response.responseText);
					if(action.failureType == Ext.form.Action.SERVER_INVALID){
						Ext.MessageBox.alert('警告', result.data.message);
					}else{
						Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
					}
				}
			}
		});
	};
};

Task = new taskJS();

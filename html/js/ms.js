//ms.js

var msJS = function(){
	var self = this;
	var server_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var server_store = new Object();		//定义全局store，方便其他方法中的调用
	
	this.ext_ms = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");

		self.server_store = new Ext.data.JsonStore({
			url : '/ms/' + param,
			root : 'data',
			//totalProperty : 'total_count',
			//remoteSort : true,
			//pruneModifiedRecords: true, 
			fields : [
				{name: 'server_id', type: 'int'},
				'server_name',
				'server_ip',
				'server_port',
				'controll_ip',
				'controll_port',
				'room_id',
				'room_name',
				'server_version',
				'protocol_version',
				'identity_file',
				'password',
				'is_valid',
				'task_number',
				'server_status1',
				'server_status2',
				'server_status3',
				'server_status4',
				'check_time'
			]
		});

		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var server_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'server_id', id : 'server_id', dataIndex : 'server_id', sortable : true},
			{header : 'server_name', id : 'server_name', dataIndex : 'server_name', sortable : true},
			{header : 'server_ip', id : 'server_ip', dataIndex : 'server_ip', sortable : true},
			{header : 'server_port', id : 'server_port', dataIndex : 'server_port', sortable : true},
			{header : 'controll_ip', id : 'controll_ip', dataIndex : 'controll_ip', sortable : true},
			{header : 'controll_port', id : 'controll_port', dataIndex : 'controll_port', sortable : true},
			{header : 'room_id', id : 'room_id', dataIndex : 'room_id', sortable : true},
			{header : 'room_name', id : 'room_name', dataIndex : 'room_name', sortable : true},
			{header : 'server_version', id : 'server_version', dataIndex : 'server_version', sortable : true},
			{header : 'protocol_version', id : 'protocol_version', dataIndex : 'protocol_version', sortable : true},
			{header : 'identity_file', id : 'identity_file', dataIndex : 'identity_file', sortable : true},
			{header : 'password', id : 'password', dataIndex : 'password', sortable : true},
			{header : 'is_valid', id : 'is_valid', dataIndex : 'is_valid', sortable : true},
			{header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
			{header : 'server_status1', id : 'server_status1', dataIndex : 'server_status1', sortable : true, renderer : server_status},
			{header : 'server_status2', id : 'server_status2', dataIndex : 'server_status2', sortable : true, renderer : server_status},
			{header : 'server_status3', id : 'server_status3', dataIndex : 'server_status3', sortable : true, renderer : server_status},
			{header : 'server_status4', id : 'server_status4', dataIndex : 'server_status4', sortable : true, renderer : server_status},
			{header : 'check_time', id : 'check_time', dataIndex : 'check_time', sortable : true, xtype: 'datecolumn', format : 'Y-m-d H:i:s'},
		]);

		self.server_store.load();
		self.server_grid = new Ext.grid.EditorGridPanel({
			id : tab_id,
			title : tab_title,
			iconCls : 'tabs',
			closable : true,
			columnLines : true,		//True表示为在列分隔处显示分隔符
			collapsible : false,		//面板是否可收缩的
			stripeRows : true,		//隔行变色
			store : self.server_store,
			colModel : server_mode,
			selModel : sel_mode,
			loadMask : {msg:'正在加载数据，请稍侯……'},
			//stateId : tab_id+'_grid'
			viewConfig : {
				forceFit:true,sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'//列按比率分配，占满整个grid
			},
			tbar : [{
				text:'刷新',
				iconCls : 'refresh',
				handler : self.refresh_server
			},'-',{
				id: 'add_server_button',
				text: '新增',
				//hidden: true,
				iconCls: 'add',
				handler: self.addServerBegin
			},'-',{
				id: 'active_server_button',
				text: '激活',
				//hidden: true,
				iconCls: 'active',
				handler: self.activeServer
			},'-',{
				id: 'stop_server_button',
				text: '停用',
				//hidden: true,
				iconCls: 'stop',
				handler: self.stopServer
			},'-',{
				id: 'show_broker_tasks',
				text: '显示任务',
				//hidden: true,
				iconCls: 'list',
				handler: self.showTasks
			}]/*,'-',{
				text:'下载报表',
				tooltip:"下载报表",
				width:75,xtype:'button',
				iconCls:'down',
				//handler:self.down_ms_csv
			},'->',{
				id: 'pc_server_global_info',
				text:'',
				xtype:'tbtext'
			}]*/
		});
		main_panel.add(self.server_grid);
		main_panel.setActiveTab(self.server_grid);

		function server_status(value) {
			switch(value) {
				case "0": return '<span class="green">0</span>'; break;
				default:
					return '<span class="red">' + value  + '</span>';
			}
		}

		//右键触发事件
		function rightClickRowMenu(grid, rowIndex, cellIndex, e) {
			e.preventDefault();//禁用浏览器默认的右键，针对某一行禁用
			if (rowIndex < 0)
				return true;
			var record = grid.getStore().getAt(rowIndex);//获取当前行的纪录
			var server_id = record.get('server_id');

			var t_sm = grid.getSelectionModel();

			//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
			//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
			var server_id_arr = []
			if (t_sm.getSelected()) {
				var recs = t_sm.getSelections();
				for (var i = 0; i < recs.length; i++) {
					server_id_arr.push(recs[i].get('server_id'));
				}
			}
			var param_id = '';
			if (server_id_arr.indexOf(server_id) < 0) {
				//当前行没有选中
				t_sm.clearSelections();
				t_sm.selectRow(rowIndex);
				grid.getView().focusRow(rowIndex);
				param_id = server_id;
			} else {
				param_id = server_id_arr.join(',');
			}

			//如果存在右键菜单，清楚菜单里的所有项
			if (Ext.get('server_right_menu')) {
				Ext.getCmp('server_right_menu').removeAll();
			}
			//生成右键菜单
			//Ext.Ajax.request({
			//	url: '/server/get_options/',
			//});
		}
		//给控键添加右键菜单触发事件
		self.server_grid.addListener('cellcontextmenu', rightClickRowMenu);
		self.server_grid.addListener('contextmenu', function(e){e.preventDefault(); })//禁用浏览器默认的右键，针对grid禁用
	};
	
	this.refresh_server = function() {
		self.server_store.reload();
	}
	
	/**
	 * 添加转码服务器
	 */
	this.addServerBegin = function() {
		if (Ext.get("add_server_info_win")) {
			Ext.getCmp("add_server_info_win").show();
			return;	//同时只存在一个添加权限信息的页面
		}
		
		var add_server_form = new Ext.FormPanel({
			id: 'add_server_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [
				{fieldLabel:'服务器IP', name:'server_ip'},
				{fieldLabel:'服务器端口', name:'server_port'},
				{fieldLabel:'服务器状态', id:'server_status', xtype:'numberfield'}
			],
			buttons: [{
				text: '增加',
				handler: self.addServerEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("add_server_info_win").close();}
			}]
		});
		
		var win = new Ext.Window({
			width:600,height:500,minWidth:400,minHeight:200,
			autoScroll:'auto',
			title : "新增转码服务器",
			id : "add_server_info_win",
			renderTo: "ext_server",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: add_server_form
		}).show();
	};
	
	this.addServerEnd = function() {
		Ext.getCmp('add_server_form').form.submit({
			waitMsg : '正在添加......',
			url : '/add_server/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("add_server_info_win").close();
				Ext.MessageBox.alert('成功', result.data);
				self.server_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
			},
			failure : function(form, action) {
				alert('失败:' + action.response.responseText);
				if(typeof(action.response) == 'undefined'){
					Ext.MessageBox.alert('警告','添加失败，请重新添加！');
				} else {
					var result = Ext.util.JSON.decode(action.response.responseText);
					if(action.failureType == Ext.form.Action.SERVER_INVALID){
						Ext.MessageBox.alert('警告', result.data);
					}else{
						Ext.MessageBox.alert('警告','表单填写异常，请重新填写！');
					}
				}
			}
		});
	};

	this.activeServer = function() {
		var grid = self.server_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var server_id_arr = []
		if (t_sm.getSelected()) {
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) {
				server_id_arr.push(recs[i].get('server_id'));
			}
		}
		//console.log(server_id_arr);

		Ext.Ajax.request({
			url: "/active_server/",
			//params:"server_ids={'server_ids': "+Ext.encode(server_id_arr)+"}",
			params:'server_ids='+server_id_arr,
			success: function(response) {
				Ext.MessageBox.alert('成功', Ext.encode(response));
				self.server_store.reload();
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};

	this.stopServer = function() {
		var grid = self.server_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var server_id_arr = []
		if (t_sm.getSelected()) {
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) {
				server_id_arr.push(recs[i].get('server_id'));
			}
		}
		//console.log(server_id_arr);

		Ext.Ajax.request({
			url: "/stop_server/",
			//params:"server_ids={'server_ids': "+Ext.encode(server_id_arr)+"}",
			params:'server_ids='+server_id_arr,
			success: function(response) {
				Ext.MessageBox.alert('成功', Ext.encode(response));
				self.server_store.reload();
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};

	this.showTasks = function() {
		var grid = self.server_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var server_id_arr = []
		if (t_sm.getSelected()) {
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) {
				server_id_arr.push(recs[i].get('server_id'));
			}
		}
		//console.log(server_id_arr);

		Ext.Ajax.request({
			url: "/set_show_broker/",
			//params:"server_ids={'server_ids': "+Ext.encode(server_id_arr)+"}",
			params:'server_ids='+server_id_arr,
			success: function(response) {
				Ext.MessageBox.alert('成功', Ext.encode(response));
				self.server_store.reload();
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
};

Ms = new msJS();

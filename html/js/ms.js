//ms.js

var msJS = function(){
	var self = this;
	var server_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var server_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	this.ext_ms = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;
		
		self.server_store = new Ext.data.JsonStore({
			url : '/get_ms_list/' + self.plat,
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
			{header : 'server_version', id : 'server_version', dataIndex : 'server_version', sortable : true, hidden: true},
			{header : 'protocol_version', id : 'protocol_version', dataIndex : 'protocol_version', sortable : true, hidden: true},
			{header : 'identity_file', id : 'identity_file', dataIndex : 'identity_file', sortable : true, hidden: true},
			{header : 'password', id : 'password', dataIndex : 'password', sortable : true, hidden: true},
			{header : 'is_valid', id : 'is_valid', dataIndex : 'is_valid', sortable : true, hidden: true},
			{header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
			{header : 'server_status1', id : 'server_status1', dataIndex : 'server_status1', sortable : true, renderer : server_status},
			{header : 'server_status2', id : 'server_status2', dataIndex : 'server_status2', sortable : true, renderer : server_status},
			{header : 'server_status3', id : 'server_status3', dataIndex : 'server_status3', sortable : true, renderer : server_status},
			{header : 'server_status4', id : 'server_status4', dataIndex : 'server_status4', sortable : true, renderer : server_status},
			{header : 'check_time', id : 'check_time', dataIndex : 'check_time', sortable : true, xtype: 'datecolumn', format : 'Y-m-d H:i:s', width: 160}
			//{header : '', id : 'null_id', dataIndex : '', sortable : flase}
		]);
			
		self.server_store.load();
		self.server_grid = new Ext.grid.EditorGridPanel({
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.server_store,
			colModel: 		server_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar : [{
				text: '同步数据库',
				iconCls: 'sync',
				handler: self.sync_ms_db
			},'-',{
				id: 'add_server_button',
				text: '刷新MS列表',				
				iconCls: 'refresh',
				handler: self.refresh_ms_list
			},'-',{
				id: 'active_server_button',
				text: 'MS详细状态',				
				iconCls: 'detail',
				handler: self.show_ms_detail
			}]
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
	
	this.sync_ms_db = function() 
	{
		Ext.Ajax.request({
			url: '/sync_ms_db/' + self.plat + '/',			
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}			
		});
	}
	
	this.refresh_ms_list = function() 
	{
		self.server_store.reload();
	}

	this.show_ms_detail = function() {
		var grid = self.server_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var ms_ips = []
		if (t_sm.getSelected()) 
		{
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) 
			{
				ms_ips.push(recs[i].get('controll_ip'));
			}
		}
		else
		{
			return;
		}
		//console.log(ms_ips);

		Ext.Ajax.request({
			url: '/show_ms_info/' + self.plat + '/',				
			params: 'ips=' + ms_ips,
			success: function(response) {
				//Ext.MessageBox.alert('成功', Ext.encode(response));	
				//console.log(response.responseText);				
				var ms_panel = new Ext.Panel({
				  //renderTo: 'panelDiv',
				  title: 'MS状态: ' + ms_ips,
				  iconCls : 'tabs',
	    		  closable : true,
	    		  autoScroll: true,
				  items:[{
				    html: response.responseText
				  }]
				});
				var main_panel = Ext.getCmp("main_panel");
				main_panel.add(ms_panel);
				main_panel.setActiveTab(ms_panel);		
				
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
};

Ms = new msJS();

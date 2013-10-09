//ms.js

var MS_PAGE_SIZE = 20;

var msJS = function(){
	var self = this;
	var server_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var server_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	this.ext_ms = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;
		
		self.server_store = new Ext.data.JsonStore({
			url: '/get_ms_list/' + self.plat + '/',			
			root: 'data',
			totalProperty: 'total_count',
			remoteSort: true,
			pruneModifiedRecords: true, 		//必须为true，这样重新reload数据时，会将脏数据清除
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
				'is_dispatch',
				'is_pause',
				'task_number',
				'server_status1',
				'server_status2',
				'server_status3',
				'server_status4',
				'total_disk_space',
				'free_disk_space',
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
			{header : 'is_dispatch', id : 'is_dispatch', dataIndex : 'is_dispatch', sortable : true, renderer : dispatch_status},
			{header : 'is_pause', id : 'is_pause', dataIndex : 'is_pause', sortable : true, renderer : pause_status},
			{header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
			{header : 'server_status1', id : 'server_status1', dataIndex : 'server_status1', sortable : true, renderer : server_status},
			{header : 'server_status2', id : 'server_status2', dataIndex : 'server_status2', sortable : true, renderer : server_status},
			{header : 'server_status3', id : 'server_status3', dataIndex : 'server_status3', sortable : true, renderer : server_status, hidden: true},
			{header : 'server_status4', id : 'server_status4', dataIndex : 'server_status4', sortable : true, renderer : server_status, hidden: true},
			{header : 'total_disk_space', id : 'total_disk_space', dataIndex : 'total_disk_space', sortable : true},
			{header : 'free_disk_space', id : 'free_disk_space', dataIndex : 'free_disk_space', sortable : true, renderer : disk_status},
			{header : 'check_time', id : 'check_time', dataIndex : 'check_time', sortable : true, xtype: 'datecolumn', format : 'Y-m-d H:i:s', width: 200}			
		]);
		
		var server_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: MS_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
	            store: self.server_store,
	            displayInfo: true,
	            displayMsg: ' 显示第{0}条 到 {1}条记录， 共 {2}条',
	            emptyMsg: "没有记录",
	            prevText: "上一页",
                nextText: "下一页",
                refreshText: "刷新",
                lastText: "最后页",
                firstText: "第一页",
                beforePageText: "当前页",
                afterPageText: "共{0}页"
		});
		
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
			tbar: [{
				id: 'sync_ms_db',
				text: '同步数据库',
				iconCls: 'sync',
				handler: self.sync_ms_db
			},'-',{
				id: 'sync_ms_status',
				text: '同步MS状态',				
				iconCls: 'sync',
				handler: self.sync_ms_status
			},'-',{
				id: 'refresh_ms_list',
				text: '刷新MS列表',				
				iconCls: 'refresh',
				handler: self.refresh_ms_list
			},'-',{
				id: 'show_ms_detail',
				text: 'MS详细状态',				
				iconCls: 'detail',
				handler: self.show_ms_detail
			}],
			listeners:{'render':createTbar},
			bbar: server_page
		});
		
		self.server_store.load({params:{start:0,limit:MS_PAGE_SIZE}});
		
		main_panel.add(self.server_grid);
		main_panel.setActiveTab(self.server_grid);			

		
		function dispatch_status(value) {
			switch(value) {
				case "0": return '<span class="red">0:不可调度</span>'; break;
				case "1": return '<span class="green">1:可调度</span>'; break;
				default:
					return '<span class="grey">' + value  + '</span>';
			}
		}
		
		function pause_status(value) {
			switch(value) {
				case "0": return '<span class="green">0:可分发</span>'; break;
				case "1": return '<span class="red">1:不可分发</span>'; break;
				default:
					return '<span class="red">' + value  + '</span>';
			}
		}
		
		function server_status(value) {
			switch(value) {
				case "0": return '<span class="green">0</span>'; break;
				default:
					return '<span class="red">' + value  + '</span>';
			}
		}
		
		function disk_status(value,metadata,record)
		{
	 		//var task_number = record.get('task_number');
	 		//var total_task_num = record.get('total_task_num');
	 		//if(task_number != total_task_num) metadata.css = 'bgred';
	 		
	 		if(value < 500) 
			{
				metadata.css = 'bgred';
			}			
			return value; 
		}
		
		//生成顶部工具条
		function createTbar(){
			var listener = {specialkey:function(field, e){if(e.getKey()==Ext.EventObject.ENTER){query_ms();}}};
			var oneTbar = new Ext.Toolbar({
				items:['server_name: ',{
						xtype:'textfield',
						id:'server_name',
						name:'server_name',
						width:110
					},"-",
					'server_ip: ',{
						xtype:'textfield',
						id:'server_ip',
						name:'server_ip',
						width:110
					},"-",
					'control_ip: ',{
						xtype:'textfield',
						id:'control_ip',
						name:'control_ip',
						width:110
					},"-",
					'room_name: ',{
						xtype:'textfield',
						id:'room_name',
						name:'room_name',
						width:110
					},"-",{
						text:'搜索',
						iconCls: 'search',
						handler: query_ms
					},"-",{
						text:'重置',
						iconCls: 'reset',
						handler: reset_query_ms
					}]
			});
			oneTbar.render(self.server_grid.tbar);
		}
		
		
		function query_ms(){			
			self.server_store.on('beforeload', function(obj) {
				Ext.apply(obj.baseParams,{
						'start':0,
						'limit':server_page.pageSize,
						'server_name':Ext.getCmp('server_name').getValue(),
						'server_ip':Ext.getCmp('server_ip').getValue(),
						'control_ip':Ext.getCmp('control_ip').getValue(),
						'room_name':Ext.getCmp('room_name').getValue()
						});
			});			
			self.server_store.load();
		};
		
		function reset_query_ms(){
			//将查询条件置为空，不可以将查询条件的充值放到beforeload里			
			Ext.getCmp('server_name').setValue("");
			Ext.getCmp('server_ip').setValue("");
			Ext.getCmp('control_ip').setValue("");
			Ext.getCmp('room_name').setValue("");
			query_ms();
		};

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
			//动态生成右键
			var menu_items = [];
			var auth_detail = {text:'MS详细状态',iconCls:'detail',handler:self.show_ms_detail};
			//var auth_modify = {text:'修改任务信息',iconCls:'modify',handler:self.modifyTaskInfo};
			var auth_refresh = {text:'刷新MS列表',iconCls:'refresh',handler:self.refresh_ms_list};
			menu_items.push(auth_detail);
			//menu_items.push(auth_modify);
			menu_items.push(auth_refresh);
			var rightMenu = new Ext.menu.Menu({
							id:'task_right_menu',
							items: menu_items
						});
			//定位。显示右键菜单
			if(e.getXY()[0]==0||e.getXY()[1]==0)
				rightMenu.show(grid.getView().getCell(rowIndex,cellIndex));
			else
				rightMenu.showAt(e.getXY());
		}
		
		
		//给控键添加右键菜单触发事件
		self.server_grid.addListener('cellcontextmenu', rightClickRowMenu);
		self.server_grid.addListener('contextmenu', function(e){e.preventDefault(); })//禁用浏览器默认的右键，针对grid禁用
		
	};
	
	/*
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
	*/
	
	this.sync_ms_db = function() 
	{
		//避免win的重复生成
		if(Ext.get("sync_ms_db_win_" + self.plat)){
			Ext.getCmp("sync_ms_db_win_" + self.plat).show();
			return true;
		}
		
		var sync_ms_db_form = new Ext.FormPanel({
			id: 'sync_ms_db_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [									
				{
				    xtype:'checkbox',
				    id: 'start_now',
				    name: 'start_now',
				    //align:'left',
				    fieldLabel:'是否立即执行',
				    checked: false
				}	
			],
			buttons: [{
				text: '确定',
				handler: self.syncMsDbEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("sync_ms_db_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:110,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "同步MS数据库",
			id : "sync_ms_db_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: sync_ms_db_form
		}).show();
	}
	
	this.syncMsDbEnd = function() {
		Ext.getCmp("sync_ms_db_form").form.submit({
			waitMsg : '正在修改......',
			url : '/sync_ms_db/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("sync_ms_db_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				//self.task_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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
	
	/*
	this.sync_ms_status = function() 
	{
		Ext.Ajax.request({
			url: '/sync_ms_status/' + self.plat + '/',			
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}			
		});
	}
	*/
	
	this.sync_ms_status = function() 
	{
		//避免win的重复生成
		if(Ext.get("sync_ms_status_win_" + self.plat)){
			Ext.getCmp("sync_ms_status_win_" + self.plat).show();
			return true;
		}
		
		var sync_ms_status_form = new Ext.FormPanel({
			id: 'sync_ms_status_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [									
				{
				    xtype:'checkbox',
				    id: 'start_now',
				    name: 'start_now',
				    //align:'left',
				    fieldLabel:'是否立即执行',
				    checked: false
				}	
			],
			buttons: [{
				text: '确定',
				handler: self.syncMsStatusEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("sync_ms_status_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:110,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "同步MS状态",
			id : "sync_ms_status_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: sync_ms_status_form
		}).show();
	}
	
	this.syncMsStatusEnd = function() {
		Ext.getCmp("sync_ms_status_form").form.submit({
			waitMsg : '正在修改......',
			url : '/sync_ms_status/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("sync_ms_status_win_" + self.plat).close();
				Ext.MessageBox.alert('成功', result.data);
				//self.task_store.reload();			//重新载入数据，即根据当前页面的条件，刷新用户页面
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

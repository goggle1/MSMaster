//room.js

var ROOM_PAGE_SIZE = 20;


var roomJS = function(){	
		
	var self = this;
	var room_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var room_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	
	
	this.ext_room = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;
		
		self.room_store = new Ext.data.JsonStore({
			url : '/get_room_list/' + self.plat + '/',
			root : 'data',
			totalProperty : 'total_count',
			remoteSort : true,
			pruneModifiedRecords: true, 
			fields : [
				{name: 'room_id', type: 'int'},
				'room_name',
				'is_valid',
				'task_number',
				'room_status',
				'num_dispatching',
				'num_deleting',
				'operation_time'
			]
		});

	
		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var room_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'room_id', id : 'room_id', dataIndex : 'room_id', sortable : true},
			{header : 'room_name', id : 'room_name', dataIndex : 'room_name', sortable : true},
			{header : 'is_valid', id : 'is_valid', dataIndex : 'is_valid', sortable : true},
			{header : 'task_number', id : 'task_number', dataIndex : 'task_number', sortable : true},
			{header : 'room_status', id : 'room_status', dataIndex : 'room_status', sortable : true},
			{header : 'num_dispatching', id : 'num_dispatching', dataIndex : 'num_dispatching', sortable : true},
			{header : 'num_deleting', id : 'num_deleting', dataIndex : 'num_deleting', sortable : true},	
			{header : 'operation_time', id : 'operation_time', dataIndex : 'operation_time', sortable : true, xtype: 'datecolumn', format : 'Y-m-d H:i:s', width: 160}	
		]);
	
		var room_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: ROOM_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
	            store: self.room_store,
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
		
		self.room_grid = new Ext.grid.EditorGridPanel({
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.room_store,
			colModel: 		room_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar: [{
				text: '同步数据库',
				iconCls: 'sync',
				handler: self.sync_room_db
			},'-',{				
				text: '刷新机房列表',				
				iconCls: 'refresh',
				handler: self.refresh_room_list
			},'-',{				
				text: '机房详细状态',				
				iconCls: 'detail',
				handler: self.show_room_detail
			}],
			bbar: room_page
		});
	
		self.room_store.load({params:{start:0,limit:ROOM_PAGE_SIZE}});
		
		main_panel.add(self.room_grid);
		main_panel.setActiveTab(self.room_grid);
	
	};
	
	this.sync_room_db = function() 
	{
		Ext.Ajax.request({
			url: '/sync_room_db/' + self.plat + '/',			
			params: '',
			success: function(response) {
				Ext.MessageBox.alert('成功', response.responseText);	
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}			
		});
	}
	
	this.refresh_room_list = function() 
	{
		self.room_store.reload();
	}

	this.show_room_detail = function() {
		var grid = self.room_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var room_ids = []
		if (t_sm.getSelected()) 
		{
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) 
			{
				room_ids.push(recs[i].get('room_id'));
			}
		}
		else
		{
			return;
		}
		//console.log(room_ids);

		Ext.Ajax.request({
			url: '/show_room_info/' + self.plat + '/',				
			params: 'ids=' + room_ids,
			success: function(response) {
				//Ext.MessageBox.alert('成功', Ext.encode(response));	
				//console.log(response.responseText);				
				var room_panel = new Ext.Panel({
				  //renderTo: 'panelDiv',
				  title: '机房状态: ' + room_ids,
				  iconCls : 'tabs',
	    		  closable : true,
	    		  autoScroll: true,
				  items:[{
				    html: response.responseText
				  }]
				});
				var main_panel = Ext.getCmp("main_panel");
				main_panel.add(room_panel);
				main_panel.setActiveTab(room_panel);		
				
			},
			failure: function(response){
				Ext.MessageBox.alert('失败', Ext.encode(response));
			}
			//timeout: (this.timeout*1000);
		});

	};
};

Room = new roomJS();

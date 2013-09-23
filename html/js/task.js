//task.js

var TASK_PAGE_SIZE = 20;

function appendZero(n)
{
	return(("00"+ n).substr(("00"+ n).length-2));
}

function formatYear(theYear)
{  
	var tmpYear = parseInt(theYear,10); 
  	if (tmpYear < 100)
  	{ 
  		tmpYear += 1900; 
  		if (tmpYear < 1940)
  		{ 
  			tmpYear += 100; 
  		} 
  	} 
  	if (tmpYear < this.MinYear)
  	{ 
  		tmpYear = this.MinYear; 
  	} 
  	if (tmpYear > this.MaxYear)
  	{ 
  		tmpYear = this.MaxYear; 
  	} 
  	return(tmpYear); 
}

function formatDate(day, formattype)
{
	var dateString = "";

 	var thisyear  = formatYear(day.getFullYear());
 	var thismonth = appendZero(day.getMonth()+1);
 	var thisday   = appendZero(day.getDate());
 	var thishour  = appendZero(day.getHours());
 	var thismin   = appendZero(day.getMinutes());
 	var thissec   = appendZero(day.getSeconds());

 	switch (formattype)
 	{
  	case 0:
   		dateString = thisyear + "年" + thismonth + "月" + thisday + "日";
   		break;
  	case 1:
   		dateString = thisyear + "-" + thismonth + "-" + thisday;
   		break;
   	case 2:
   		dateString = thisyear + thismonth + thisday;
   		break;
  	case 3:
   		dateString = thisyear + "-" + thismonth + "-" + thisday+ " " + appendZero(thishour) + ":" + appendZero(thismin) + ":" + appendZero(thissec);
   		break;
  	default:
   		dateString = thisyear + "-" + thismonth + "-" + thisday;
 	}
 	return dateString;
}
	
function getDiffDate(dadd,formattype)
{
	//可以加上错误处理
 	var a = new Date();
 	a = a.valueOf();
 	a = a + dadd * 24 * 60 * 60 * 1000;
 	a = new Date(a);
 	return formatDate(a, formattype);
}

var taskJS = function(){
	var self = this;
	var task_grid = new Object();		//定义全局grid，方便其他方法中的调用
	var task_store = new Object();		//定义全局store，方便其他方法中的调用
	var plat = '';
	
	this.ext_task = function(tab_id, tab_title, param){
		var main_panel = Ext.getCmp("main_panel");
		self.plat = param;

		self.task_store = new Ext.data.JsonStore({
			url : '/get_task_list/' + self.plat + '/',
			root : 'data',
			totalProperty : 'total_count',
			remoteSort : true,
			pruneModifiedRecords: true, 
			fields : [
				{name: 'hash', type: 'string'},
				'online_time',
				'is_valid',
				'hot',
				'cold1',
				'cold2',
				'cold3',
				'last_hit_time',
				'total_hits_num'
			]
		});

		var sel_mode = new Ext.grid.CheckboxSelectionModel();
		var task_mode = new Ext.grid.ColumnModel([
			new Ext.grid.RowNumberer(),
			sel_mode,
			{header : 'hash', id : 'hash', dataIndex : 'hash', sortable : true},
			{header : 'online_time', id : 'online_time', dataIndex : 'online_time', sortable : true},
			{header : 'is_valid', id : 'hot', dataIndex : 'hot', sortable : true, hidden: true},
			{header : 'hot', id : 'hot', dataIndex : 'hot', sortable : true},
			{header : 'cold1', id : 'cold1', dataIndex : 'cold1', sortable : true},
			{header : 'cold2', id : 'cold2', dataIndex : 'cold2', sortable : true},
			{header : 'cold3', id : 'cold3', dataIndex : 'cold3', sortable : true},
			{header : 'last_hit_time', id : 'last_hit_time', dataIndex : 'last_hit_time', sortable : true},
			{header : 'total_hits_num', id : 'total_hits_num', dataIndex : 'total_hits_num', sortable : true, width: 150}
		]);
		
		var task_page = new Ext.PagingToolbar({
				plugins: [new Ext.ui.plugins.SliderPageSize(), new Ext.ui.plugins.ComboPageSize({ addToItem: false, prefixText: '每页', postfixText: '条'}),new Ext.ux.ProgressBarPager()],
				//plugins: [new Ext.ui.plugins.SliderPageSize()],
	            pageSize: TASK_PAGE_SIZE,		//每页要展现的记录数，默认从定义的全局变量获取
	            store: self.task_store,
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

		self.task_grid = new Ext.grid.EditorGridPanel({
			id: 			tab_id,
			title: 			tab_title,
			iconCls: 		'tabs',
			clicksToEdit: 	2,
			autoScroll: 	true,		//内容溢出时出现滚动条
			closable: 		true,
			columnLines: 	true,		//True表示为在列分隔处显示分隔符
			collapsible: 	false,		//面板是否可收缩的
			stripeRows: 	true,		//隔行变色
			store: 			self.task_store,
			colModel: 		task_mode,
			selModel: 		sel_mode,
			loadMask: 		{ msg: '正在加载数据，请稍侯……' },
			//stateId: tab_id+'_grid'
			viewConfig : {
				forceFit:true, sortAscText:'升序',sortDescText:'降序',columnsText:'可选列'
			},
			tbar: [{
				text: '同步hash库',
				iconCls: 'sync',
				handler: self.sync_hash_db
			},'-',{
				text: '导入点击量',
				iconCls: 'upload',
				handler: self.upload_hits_num
			},'-',{
				text: '计算冷度',
				iconCls: 'chart',
				handler: self.calc_cold
			},'-',{
				text: '导出热度表',
				iconCls: 'compare_down',
				handler: self.down_hot_table
			},'-',{
				text: '导出冷度表',
				iconCls: 'compare_down',
				handler: self.down_cold_table
			},'-',{				
				text: '刷新任务列表',				
				iconCls: 'refresh',
				handler: self.refresh_task_list
			},'-',{				
				text: '任务详细状态',				
				iconCls: 'detail',
				handler: self.show_task_detail
			}],
			bbar: task_page
		});
	
		self.task_store.load({params:{start:0, limit:TASK_PAGE_SIZE}});
		
		main_panel.add(self.task_grid);
		main_panel.setActiveTab(self.task_grid);
	};

	/**
	 * 刷新列表
	 */
	this.refresh_task_list = function() {
		self.task_store.reload();
	}
	
	/*
	this.sync_hash_db = function() 
	{		
		Ext.Ajax.request({
			timeout: 60, // 60 seconds
			url: '/sync_hash_db/' + self.plat + '/',			
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
	
	
	this.sync_hash_db = function(){
		//避免win的重复生成
		if(Ext.get("sync_hash_db_win_" + self.plat)){
			Ext.getCmp("sync_hash_db_win_" + self.plat).show();
			return true;
		}
		
		var yesterday = getDiffDate(-1, 2);
		
		var sync_hash_db_form = new Ext.FormPanel({
			id: 'sync_hash_db_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [				
				{
					fieldLabel:'begin_date',	
					name: 'begin_date', 
					value: yesterday, 
					allowBlank: true,
					blankText: '开始日期可以为空'
				},
				{
					fieldLabel:'end_date',	
					name: 'end_date', 
					value: '', 
					allowBlank: true,
					blankText: '截止日期可以为空'
				},					
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
				handler: self.syncHashDbEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("sync_hash_db_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:160,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "同步hash库",
			id : "sync_hash_db_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: sync_hash_db_form
		}).show();		
		
	};
	
	
	this.syncHashDbEnd = function() {
		Ext.getCmp("sync_hash_db_form").form.submit({
			waitMsg : '正在修改......',
			url : '/sync_hash_db/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("sync_hash_db_win_" + self.plat).close();
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
	this.upload_hits_num = function() 
	{		
		var yesterday = getDiffDate(-1, 2);
		Ext.MessageBox.prompt('上传点击量', '请输入日期：', upload_tasks, this, false, yesterday);
		function upload_tasks(e, text){
			if(e == "cancel")return true;
			if(isNaN(text)){
				Ext.Msg.alert("警告", "输入参数不正确，请输入日期！");
				return false;
			}
			Ext.Ajax.request({
				timeout: 60, //60 seconds
				url: '/upload_hits_num/' + self.plat + '/',			
				params: 'date=' + text,
				success: function(response) {
					Ext.MessageBox.alert('成功', response.responseText);	
				},
				failure: function(response){
					Ext.MessageBox.alert('失败', Ext.encode(response));
				}			
			});
		}		
		
	}
	*/
	
	this.upload_hits_num = function(){
		//避免win的重复生成
		if(Ext.get("upload_hits_num_win_" + self.plat)){
			Ext.getCmp("upload_hits_num_win_" + self.plat).show();
			return true;
		}
		
		var yesterday = getDiffDate(-1, 2);
		
		var upload_hits_num_form = new Ext.FormPanel({
			id: 'upload_hits_num_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [				
				{
					fieldLabel:'begin_date',	
					name: 'begin_date', 
					value: yesterday, 
					allowBlank: false,
					blankText: '开始日期不能为空'
				},
				{
					fieldLabel:'end_date',	
					name: 'end_date', 
					value: '', 
					allowBlank: true,
					blankText: '截止日期可以为空'
				},					
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
				handler: self.uploadHitsNumEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("upload_hits_num_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:160,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "上传点击量",
			id : "upload_hits_num_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: upload_hits_num_form
		}).show();		
		
	};
	
	
	this.uploadHitsNumEnd = function() {
		Ext.getCmp("upload_hits_num_form").form.submit({
			waitMsg : '正在修改......',
			url : '/upload_hits_num/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("upload_hits_num_win_" + self.plat).close();
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
	this.calc_cold = function() 
	{		
		Ext.Ajax.request({
			timeout: 60, // 60 seconds
			url: '/calc_cold/' + self.plat + '/',			
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
	
	this.calc_cold = function(){
		//避免win的重复生成
		if(Ext.get("calc_cold_win_" + self.plat)){
			Ext.getCmp("calc_cold_win_" + self.plat).show();
			return true;
		}
				
		
		var calc_cold_form = new Ext.FormPanel({
			id: 'calc_cold_form',
			autoWidth: true,//自动调整宽度
			url:'',
			frame:true,
			monitorValid : true,
			bodyStyle:'padding:5px 5px 0',
			labelWidth:150,
			defaults:{xtype:'textfield',width:200},
			items: [				
			/*	{
					fieldLabel:'begin_date',	
					name: 'begin_date', 
					value: yesterday, 
					allowBlank: false,
					blankText: '开始日期不能为空'
				},
				{
					fieldLabel:'end_date',	
					name: 'end_date', 
					value: '', 
					allowBlank: true,
					blankText: '截止日期可以为空'
				},	*/				
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
				handler: self.calcColdEnd,
				formBind : true
			},{
				text: '取消',
				handler: function(){Ext.getCmp("calc_cold_win_" + self.plat).close();}
			}]
		});
		
		var win = new Ext.Window({
			width:400,height:110,minWidth:200,minHeight:100,
			autoScroll:'auto',
			title : "计算冷度",
			id : "calc_cold_win_" + self.plat,
			//renderTo: "ext_room",
			collapsible: true,
			modal:false,	//True 表示为当window显示时对其后面的一切内容进行遮罩，false表示为限制对其它UI元素的语法（默认为 false
			//所谓布局就是指容器组件中子元素的分布，排列组合方式
			layout: 'form',//layout布局方式为form
			maximizable:true,
			minimizable:false,
			items: calc_cold_form
		}).show();		
		
	};
	
	
	this.calcColdEnd = function() {
		Ext.getCmp("calc_cold_form").form.submit({
			waitMsg : '正在修改......',
			url : '/calc_cold/' + self.plat + '/',
			method : 'post',
			timeout : 5000,//5秒超时, 
			params : '',
			success : function(form, action) {
				var result = Ext.util.JSON.decode(action.response.responseText);
				Ext.getCmp("calc_cold_win_" + self.plat).close();
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
	
	this.down_hot_table = function(){
		var pre_task_num = 20000;
		Ext.MessageBox.prompt('下载热门任务列表', '请输入任务总数（整数）', down_hot_tasks, this, false, pre_task_num);
		function down_hot_tasks(e, text){
			if(e == "cancel")return true;
			if(isNaN(text)){
				Ext.Msg.alert("警告", "输入参数不正确，请输入数字！");
				return false;
			}
			var url = "/down_hot_tasks/" + self.plat + "/";
			url = url + "?task_num=" + text;
			location.href = url;
		}
	};
	
	this.down_cold_table = function(){
		var pre_task_num = 20000;
		Ext.MessageBox.prompt('下载冷门任务列表', '请输入任务总数（整数）', down_cold_tasks, this, false, pre_task_num);
		function down_cold_tasks(e, text){
			if(e == "cancel")return true;
			if(isNaN(text)){
				Ext.Msg.alert("警告", "输入参数不正确，请输入数字！");
				return false;
			}
			var url = "/down_cold_tasks/" + self.plat + "/";
			url = url + "?task_num=" + text;
			location.href = url;
		}
	};
	
	this.show_task_detail = function() {
		var grid = self.task_grid;
		var t_sm = grid.getSelectionModel();

		//此处为多选行，如果没有选中任意一行时，需要对右键当前行进行选中设置
		//如果右键当前行不在选中的行中，则移除所选的行，选择当前行
		var task_hashs = []
		if (t_sm.getSelected()) 
		{
			var recs = t_sm.getSelections();
			for (var i = 0; i < recs.length; i++) 
			{
				task_hashs.push(recs[i].get('hash'));
			}
		}
		else
		{
			return;
		}
		//console.log(ms_ips);

		Ext.Ajax.request({
			url: '/show_task_info/' + self.plat + '/',				
			params: 'hashs=' + task_hashs,
			success: function(response) {
				//Ext.MessageBox.alert('成功', Ext.encode(response));	
				//console.log(response.responseText);				
				var ms_panel = new Ext.Panel({
				  //renderTo: 'panelDiv',
				  title: '任务信息: ' + task_hashs,
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

Task = new taskJS();

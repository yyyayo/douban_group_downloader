本代码主要是为了在豆瓣关闭私密小组前备份所有帖子。所有帖子下载后目录会组织为：
```
groupname_grouid
├── post_1_tile
│   ├── 1.html
│   └── 2.html
└── post_2_tile
    └── 1.html
```

下载前先配置 ``config.json`` 文件。
首先需要配置用于登录的用户名 ``username`` 和密码 ``password`` ，请确保此用户名密码拥有要下载的小组的权限。
此外， ``groupid`` 指的是小组网址中显示的 ID 。例如【无用美学小组】的网址为：https://www.douban.com/group/699356/ ，则可以配置为：
```
{
	"groupid": "699356",
	"groupname": "无用美学小组"
}
```

配置后直接 python3 运行 ``douban_private_spider.py`` 即可。
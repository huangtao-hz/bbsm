create table if not exists bbsm(
    rq      text,   -- 日期
    xm      text,   -- 系统或项目
    jym     text,   -- 交易码
    jymc    text,   -- 交易名称
    nr      text,   -- 测试内容
    yhyy    text,   -- 优化原因
    yzjg    text,   -- 验证机构
    wcsj    text,   -- 完成时间
    yzyq    text,   -- 验证要求
    lxr     text,   -- 联系人
    yzsj    time    -- 验证时间
);
create index if not exists bbsm_jym on bbsm(jym);
create index if not exists bbsm_rq on bbsm(rq);


create table if not exists yzanpai(
    fh      text,   -- 验证分行
    rq      text,   -- 验证日期
    nr      text,   -- 验证内容  0-季版本，1-月版本，2-周版本，3-其他验证
    primary key(fh,rq)
);


create table if not exists ysnr(
    tcrq    text,   -- 投产日期
    xmbh    text,   -- 项目编号
    xmjl    text,   -- 项目经理
    tmbh    text,   -- 条目编号
    gnmc    text,   -- 功能名称
    gngs    text,   -- 功能概述
    glxt    text,   -- 关联系统
    csjl    text,   -- 测试经理
    cslxr   text,   -- 测试联系人
    xrtcr   text,   -- 需求提出人
    ysry    text    -- 验收人员
);

-- 运营管理部人员名单
create table if not exists rymd(
    zx      text,  -- 中心
    xm      text,   -- 姓名
    zg      text    -- 主管
);

create index if not exists rymd_xm on rymd(xm);


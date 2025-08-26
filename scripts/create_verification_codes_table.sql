-- 创建验证码表
drop table if exists soluna.verification_codes;
create table soluna.verification_codes (
    id bigint auto_increment primary key comment '主键ID',
    phone_number varchar(20) not null comment '手机号码',
    verification_code varchar(10) not null comment '验证码',
    ip_address varchar(50) not null default 'unknown' comment '请求IP地址',
    created_at datetime not null default current_timestamp comment '创建时间',
    expire_time datetime not null comment '过期时间',
    is_used tinyint not null default 0 comment '是否已使用(0:未使用,1:已使用)',
    constraint idx_phone_created_at unique (phone_number, created_at)
) comment '验证码表';

-- 添加索引以提高查询性能
alter table soluna.verification_codes add index idx_phone_number (phone_number);
alter table soluna.verification_codes add index idx_ip_address (ip_address);
alter table soluna.verification_codes add index idx_expire_time (expire_time);
alter table soluna.verification_codes add index idx_is_used (is_used);
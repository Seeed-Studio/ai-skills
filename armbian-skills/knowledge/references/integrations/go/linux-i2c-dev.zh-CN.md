---
schema_version: '1'
id: integration.go.linux-i2c-dev
kind: integration
applies_to:
  languages:
  - go
  capabilities:
  - i2c
  stack_ids:
  - linux-i2c-dev
required_refs:
- integration.go.guide
- stack.linux-i2c-dev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-i2c-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](linux-i2c-dev.md) | [简体中文](linux-i2c-dev.zh-CN.md)

# go / linux-i2c-dev

I2C 优先采用已有内核器件驱动公开接口。裸 i2c-dev 需匹配传感器协议、能力检查、地址与组合事务语义；只实现目标器件需要的事务，不扫描内部总线。读数失败/超时保留错误和过期时间戳，不能把上次值当新读数。

具体库与锁定版本在用户项目实施时查证，不声明已验证任意第三方绑定。配置使用当前解析的adapter/controller和器件地址，不把其他板卡节点硬编码进通用源码；I2C地址不能写成GPIO line。I2C_SLAVE避免使用FORCE；协作进程锁不等于整个总线独占，也不能取代内核地址占用检查。

已有服务把采集接到原业务API并保留旧功能；HTTP处理器只读缓存，硬件调用不长期持有缓存锁。失败保留最后成功数据及原时间/序号，显式报告错误/过期；新鲜度用单调时间，设备UTC时钟是否校准另记。Go context不能自动打断阻塞的内核I2C调用；需要任务期限时按驱动/项目选择可控工作进程等方案，前一个I/O owner未确认退出前不叠加重试。不可中断内核I/O不能由用户态保证立即终止。

手册可能用8位线级读写地址而API接收7位地址，先核对；例如AHT20的0x71是0x38的读地址，不需作为payload再次写入。短读不能盲目用io.ReadFull拼接，第二次read可能已是新事务；是否使用组合事务/重复起始由实际器件决定。

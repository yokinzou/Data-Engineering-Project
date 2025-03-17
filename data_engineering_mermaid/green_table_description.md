```
| Field Name             | Description                                                                 | 中文意思                                                                 |
|:-----------------------|:-----------------------------------------------------------------------------|:-------------------------------------------------------------------------|
| VendorID               | A code indicating the TPEP provider that provided the record.               | 记录提供者的代码。1=Creative Mobile Technologies, LLC；2=VeriFone Inc.     |
| tpep_pickup_datetime   | The date and time when the meter was engaged.                                | 计价器启动的日期和时间                                                   |
| tpep_dropoff_datetime  | The date and time when the meter was disengaged.                             | 计价器关闭的日期和时间                                                   |
| Passenger_count        | The number of passengers in the vehicle. This is a driver-entered value.     | 车内的乘客数量。这是司机输入的值                                         |
| Trip_distance          | The elapsed trip distance in miles reported by the taximeter.               | 计价器报告的行程距离（英里）                                             |
| PULocationID           | TLC Taxi Zone in which the taximeter was engaged                            | 计价器启动的 TLC 出租车区域                                              |
| DOLocationID           | TLC Taxi Zone in which the taximeter was disengaged                         | 计价器关闭的 TLC 出租车区域                                              |
| RateCodeID             | The final rate code in effect at the end of the trip.                       | 行程结束时生效的最终费率代码。1=标准费率；2=JFK；3=纽瓦克；4=拿骚或韦斯特切斯特；5=议价；6=合乘 |
| Store_and_fwd_flag     | This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka “store and forward,” because the vehicle did not have a connection to the server. | 此标志表示行程记录是否因车辆与服务器没有连接而被存储在车辆内存中，然后再发送给供应商，即“存储转发”行程。Y=存储转发行程；N=非存储转发行程 |
| Payment_type           | A numeric code signifying how the passenger paid for the trip.               | 表示乘客支付行程的数字代码。1=信用卡；2=现金；3=免费；4=争议；5=未知；6=作废行程 |
| Fare_amount            | The time-and-distance fare calculated by the meter.                         | 计价器计算的时间和距离费用                                               |
| Extra                  | Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges. | 目前仅包括 0.5 美元和 1 美元的高峰时段和夜间附加费                         |
| MTA_tax                | $0.50 MTA tax that is automatically triggered based on the metered rate in use. | 根据使用的计价器费率自动触发的 0.5 美元 MTA 税                             |
| Improvement_surcharge  | $0.30 improvement surcharge assessed trips at the flag drop. The improvement surcharge began being levied in 2015. | 在行程开始时征收的 0.3 美元改进附加费。改进附加费自 2015 年开始征收         |
| Tip_amount             | Tip amount – This field is automatically populated for credit card tips. Cash tips are not included. | 小费金额——此字段会自动记录信用卡小费。现金小费不包括在内                   |
| Tolls_amount           | Total amount of all tolls paid in trip.                                      | 行程中支付的所有过路费总额                                               |
| Total_amount           | The total amount charged to passengers. Does not include cash tips.          | 向乘客收取的总金额。不包括现金小费                                       |
| Congestion_Surcharge   | Total amount collected in trip for NYS congestion surcharge.                | 行程中收取的纽约州拥堵附加费总额                                         |
| Airport_fee            | $1.25 for pick up only at LaGuardia and John F. Kennedy Airports             | 仅在拉瓜迪亚机场和约翰·肯尼迪机场接客时收取的 1.25 美元机场费             |
```


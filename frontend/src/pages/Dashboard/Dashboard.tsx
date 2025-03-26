import React from 'react';
import { Card, Row, Col, Typography, Segmented } from 'antd';
import { useState } from 'react';
import { Line, Pie } from '@ant-design/charts';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  const [errorPeriod, setErrorPeriod] = useState<string | number>('Weekly');
  const [knowledgePeriod, setKnowledgePeriod] = useState<string | number>('Weekly');
  const [ratioType, setRatioType] = useState<string | number>('高数');

  // 错题数据图表配置
  const errorConfig = {
    data: [
      { day: 'Sun', 高数: 4200, 线代: 2800, 概率论: 1500 },
      { day: 'Mon', 高数: 3500, 线代: 2500, 概率论: 2000 },
      { day: 'Tue', 高数: 2800, 线代: 2000, 概率论: 1800 },
      { day: 'Wed', 高数: 3800, 线代: 2800, 概率论: 1100 },
      { day: 'Thu', 高数: 4800, 线代: 3300, 概率论: 1900 },
      { day: 'Fri', 高数: 3900, 线代: 2500, 概率论: 2100 },
      { day: 'Sat', 高数: 4500, 线代: 3000, 概率论: 2200 },
    ],
    xField: 'day',
    yField: 'value',
    seriesField: 'category',
    legend: { position: 'top' },
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
  };

  // 知识点数据图表配置
  const knowledgeConfig = {
    data: [
      { day: 'Sun', 高数: 4500, 线代: 3000, 概率论: 1800 },
      { day: 'Mon', 高数: 3800, 线代: 2700, 概率论: 2100 },
      { day: 'Tue', 高数: 3200, 线代: 2200, 概率论: 1600 },
      { day: 'Wed', 高数: 4100, 线代: 3000, 概率论: 1000 },
      { day: 'Thu', 高数: 5000, 线代: 3500, 概率论: 2000 },
      { day: 'Fri', 高数: 4200, 线代: 2700, 概率论: 2200 },
      { day: 'Sat', 高数: 4700, 线代: 3200, 概率论: 2300 },
    ],
    xField: 'day',
    yField: 'value',
    seriesField: 'category',
    legend: { position: 'top' },
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
  };

  // 知识点占比图表配置
  const ratioConfig = {
    data: [
      { type: 'chapter 1', value: 546 },
      { type: 'chapter 2', value: 457 },
      { type: 'chapter 3', value: 386 },
      { type: 'chapter 4', value: 64 },
    ],
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    innerRadius: 0.64,
    label: {
      type: 'inner',
      offset: '-30%',
      content: '{value}',
      style: {
        textAlign: 'center',
      },
    },
    statistic: {
      title: {
        content: '知识点总数',
        style: {
          fontSize: '14px',
        },
      },
      content: {
        content: '1,500',
        style: {
          fontSize: '24px',
        },
      },
    },
  };

  // 准备折线图数据
  const prepareLineData = (rawData: Array<Record<string, string | number>>) => {
    const result: Array<{day: string, value: number, category: string}> = [];
    rawData.forEach(item => {
      Object.keys(item).forEach(key => {
        if (key !== 'day') {
          result.push({
            day: item.day as string,
            value: item[key] as number,
            category: key
          });
        }
      });
    });
    return result;
  };

  return (
    <div className="dashboard-page">
      <Title level={2}>仪表盘</Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="错题总数" bordered={false}>
            <Title level={2}>4,168</Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="知识点总数" bordered={false}>
            <Title level={2}>1,500</Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="已解决" bordered={false}>
            <Title level={2}>3,542</Title>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="待解决" bordered={false}>
            <Title level={2}>626</Title>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card 
            title="新增错题数量" 
            bordered={false}
            extra={
              <Segmented 
                options={['Daily', 'Weekly', 'Monthly']} 
                value={errorPeriod}
                onChange={setErrorPeriod}
              />
            }
          >
            <div style={{ height: '350px' }}>
              <Line {...errorConfig} data={prepareLineData(errorConfig.data)} />
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card 
            title="新增知识点数量" 
            bordered={false}
            extra={
              <Segmented 
                options={['Daily', 'Weekly', 'Monthly']} 
                value={knowledgePeriod}
                onChange={setKnowledgePeriod}
              />
            }
          >
            <div style={{ height: '350px' }}>
              <Line {...knowledgeConfig} data={prepareLineData(knowledgeConfig.data)} />
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24}>
          <Card 
            title="知识点占比" 
            bordered={false}
            extra={
              <Segmented 
                options={['高数', '线代', '概率论']} 
                value={ratioType}
                onChange={setRatioType}
              />
            }
          >
            <div style={{ height: '350px' }}>
              <Pie {...ratioConfig} />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 
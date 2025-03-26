import React from 'react';
import { Typography, Row, Col, Breadcrumb } from 'antd';
import { HomeOutlined, FileTextOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import ErrorSubmitForm from '../../components/business/ErrorSubmitForm';

const { Title } = Typography;

const QuestionCreate: React.FC = () => {
  return (
    <div className="question-create-page">
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={2}>创建错题</Title>
        </Col>
        <Col>
          <Breadcrumb items={[
            {
              title: <Link to="/"><HomeOutlined /> 首页</Link>,
            },
            {
              title: <Link to="/questions"><FileTextOutlined /> 错题管理</Link>,
            },
            {
              title: '创建错题',
            },
          ]} />
        </Col>
      </Row>

      <Row>
        <Col xs={24} sm={24} md={20} lg={16} xl={14}>
          <ErrorSubmitForm />
        </Col>
      </Row>
    </div>
  );
};

export default QuestionCreate; 
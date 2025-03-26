import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Tabs, Row, Col, Space } from 'antd';
import { QuestionOutlined, CameraOutlined, FormOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import ErrorImageUploader from './ErrorImageUploader';
import { questionsAPI } from '../../api/questions';

const { TextArea } = Input;
const { TabPane } = Tabs;

interface ErrorFormValues {
  content: string;
  remarks?: string;
}

const ErrorSubmitForm: React.FC = () => {
  const [form] = Form.useForm<ErrorFormValues>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [activeTab, setActiveTab] = useState<string>('text');

  // 处理OCR识别出的文本
  const handleExtractedTextChange = (text: string) => {
    form.setFieldsValue({ content: text });
  };

  // 处理图片URL变更
  const handleImageUrlChange = (url: string) => {
    setImageUrl(url);
  };

  // 处理表单提交
  const handleSubmit = async (values: ErrorFormValues) => {
    try {
      setLoading(true);
      
      // 构建错题数据
      const questionData = {
        ...values,
        image_url: imageUrl
      };
      
      // 提交错题数据到API
      await questionsAPI.createQuestion(questionData);
      
      message.success('错题提交成功！');
      form.resetFields();
      setImageUrl('');
      
      // 提交成功后跳转到错题列表页
      navigate('/questions');
    } catch (error) {
      console.error('提交错误:', error);
      message.error('提交失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title={
        <Space>
          <QuestionOutlined />
          <span>提交错题</span>
        </Space>
      }
      bordered={false}
      className="error-submit-card"
    >
      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
      >
        <TabPane 
          tab={<span><FormOutlined /> 直接输入</span>} 
          key="text"
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{ content: '', remarks: '' }}
          >
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item
                  name="content"
                  label="错题内容"
                  rules={[{ required: true, message: '请输入错题内容' }]}
                >
                  <TextArea 
                    rows={6} 
                    placeholder="请输入错题内容..."
                  />
                </Form.Item>
              </Col>
              
              <Col span={24}>
                <Form.Item
                  name="remarks"
                  label="备注"
                >
                  <TextArea 
                    rows={4} 
                    placeholder="可选：添加备注、错误原因..."
                  />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                block
              >
                提交错题
              </Button>
            </Form.Item>
          </Form>
        </TabPane>
        
        <TabPane 
          tab={<span><CameraOutlined /> 上传图片</span>} 
          key="image"
        >
          <ErrorImageUploader 
            onExtractedTextChange={handleExtractedTextChange}
            onImageUrlChange={handleImageUrlChange}
          />
          
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            style={{ marginTop: 16 }}
          >
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item
                  name="content"
                  label="识别内容"
                  rules={[{ required: true, message: '请输入错题内容' }]}
                >
                  <TextArea 
                    rows={6} 
                    placeholder="如果识别结果不准确，可手动调整"
                  />
                </Form.Item>
              </Col>
              
              <Col span={24}>
                <Form.Item
                  name="remarks"
                  label="备注"
                >
                  <TextArea 
                    rows={4} 
                    placeholder="可选：添加备注、错误原因..."
                  />
                </Form.Item>
              </Col>
            </Row>
            
            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                block
              >
                提交错题
              </Button>
            </Form.Item>
          </Form>
        </TabPane>
      </Tabs>
    </Card>
  );
};

export default ErrorSubmitForm; 
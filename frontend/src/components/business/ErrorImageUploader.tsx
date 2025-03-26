import React, { useState } from 'react';
import { Card, Typography, Spin } from 'antd';
import ImageUploader from '../common/ImageUploader';
import { imageAPI } from '../../api/image';

const { Title, Paragraph } = Typography;

interface ErrorImageUploaderProps {
  onExtractedTextChange?: (text: string) => void;
  onImageUrlChange?: (url: string) => void;
}

const ErrorImageUploader: React.FC<ErrorImageUploaderProps> = ({
  onExtractedTextChange,
  onImageUrlChange
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [extractedText, setExtractedText] = useState<string>('');

  const handleUpload = async (file: File): Promise<string> => {
    setLoading(true);
    try {
      // 调用API上传图片并获取OCR结果
      const response = await imageAPI.processImage(file);
      
      // 设置提取的文本
      setExtractedText(response.data.text);
      if (onExtractedTextChange) {
        onExtractedTextChange(response.data.text);
      }
      
      // 返回图片URL
      if (onImageUrlChange) {
        onImageUrlChange(response.data.image_url);
      }
      
      return response.data.image_url;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="error-image-uploader">
      <Card
        title="错题图片上传"
        extra={<span>上传图片可自动识别题目内容</span>}
      >
        <Spin spinning={loading} tip="正在识别图片文字...">
          <ImageUploader 
            onUpload={handleUpload}
            value={imageUrl}
            onChange={setImageUrl}
          />
          
          {extractedText && (
            <div style={{ marginTop: 16 }}>
              <Title level={5}>识别结果:</Title>
              <Card>
                <Paragraph>{extractedText}</Paragraph>
              </Card>
            </div>
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default ErrorImageUploader; 
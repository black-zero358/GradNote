import React, { useState } from 'react';
import { Upload, Button, message, Image } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';

interface ImageUploaderProps {
  onUpload: (file: File) => Promise<string>;
  value?: string;
  onChange?: (value: string) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onUpload, value, onChange }) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [imageUrl, setImageUrl] = useState<string>(value || '');
  const [loading, setLoading] = useState<boolean>(false);

  const handleUpload = async (file: File) => {
    try {
      setLoading(true);
      const url = await onUpload(file);
      setImageUrl(url);
      if (onChange) {
        onChange(url);
      }
      message.success('上传成功');
    } catch (error) {
      message.error('上传失败');
      console.error('上传错误:', error);
    } finally {
      setLoading(false);
      setFileList([]);
    }
  };

  const uploadProps: UploadProps = {
    fileList,
    beforeUpload: (file) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('只能上传图片文件!');
        return false;
      }
      
      const isLt5M = file.size / 1024 / 1024 < 5;
      if (!isLt5M) {
        message.error('图片不能超过5MB!');
        return false;
      }

      setFileList([...fileList, file as UploadFile]);
      handleUpload(file);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setFileList([]);
      setImageUrl('');
      if (onChange) {
        onChange('');
      }
    },
  };

  return (
    <div className="image-uploader">
      <Upload {...uploadProps} listType="picture">
        <Button 
          icon={<UploadOutlined />} 
          loading={loading}
          disabled={fileList.length > 0 || loading}
        >
          选择图片
        </Button>
      </Upload>
      
      {imageUrl && (
        <div style={{ marginTop: 16 }}>
          <Image 
            src={imageUrl} 
            alt="上传的图片" 
            style={{ maxWidth: '100%', maxHeight: '300px' }} 
          />
        </div>
      )}
    </div>
  );
};

export default ImageUploader; 
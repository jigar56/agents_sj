import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  FormControl,
  FormLabel,
  Input,
  Button,
  useToast,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from 'react-query';
import { launchAPI } from '../services/api';

export default function CreateLaunch() {
  const [formData, setFormData] = useState({
    name: '',
  });
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();

  const createLaunchMutation = useMutation(launchAPI.createLaunch, {
    onSuccess: (data) => {
      toast({
        title: 'Launch created',
        description: 'Your launch has been created successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      queryClient.invalidateQueries('launches');
      navigate(`/launches/${data.id}`);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to create launch.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a launch name.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    createLaunchMutation.mutate(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading>Create New Launch</Heading>

        <Box bg="white" p={6} rounded="lg" shadow="sm">
          <form onSubmit={handleSubmit}>
            <VStack spacing={6} align="stretch">
              <FormControl isRequired>
                <FormLabel>Launch Name</FormLabel>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter a name for your product launch"
                  size="lg"
                />
              </FormControl>

              <Alert status="info">
                <AlertIcon />
                This will create a new launch workflow that will be processed by our AI agents:
                Market Research → Timeline Planning → Communications Strategy → Feedback & Optimization
              </Alert>

              <VStack spacing={3}>
                <Button
                  type="submit"
                  colorScheme="brand"
                  size="lg"
                  width="full"
                  isLoading={createLaunchMutation.isLoading}
                  loadingText="Creating Launch..."
                >
                  Create Launch
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  width="full"
                  onClick={() => navigate('/')}
                >
                  Cancel
                </Button>
              </VStack>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Container>
  );
}

import React from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Spinner,
  Alert,
  AlertIcon,
  Progress,
  useToast,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react';
import { useParams, Link as RouterLink, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { FiPlay, FiClock, FiCheckCircle, FiXCircle, FiArrowLeft, FiTrash2 } from 'react-icons/fi';
import { launchAPI } from '../services/api';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    pending: { color: 'yellow', icon: FiClock },
    in_progress: { color: 'blue', icon: FiPlay },
    completed: { color: 'green', icon: FiCheckCircle },
    failed: { color: 'red', icon: FiXCircle },
  };

  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <Badge colorScheme={config.color} display="flex" alignItems="center" gap={1}>
      <Icon size={12} />
      {status.replace('_', ' ').toUpperCase()}
    </Badge>
  );
};

const AgentResultCard = ({ result }) => {
  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="sm" textTransform="capitalize">
            {result.agent_name ? result.agent_name.replace('_', ' ') : 'Unknown'} Agent
          </Heading>
          <StatusBadge status={result.status} />
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack align="start" spacing={3}>
          <Text fontSize="sm" color="gray.600">
            {new Date(result.timestamp).toLocaleString()}
          </Text>
          {result.error_flag && (
            <Alert status="error" size="sm">
              <AlertIcon />
              {result.error_message}
            </Alert>
          )}
          {result.output && (
            <Accordion allowToggle width="full">
              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <Text fontSize="sm" fontWeight="medium">
                        View Output
                      </Text>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <Box
                    bg="gray.50"
                    p={3}
                    rounded="md"
                    fontSize="sm"
                    whiteSpace="pre-wrap"
                    maxH="200px"
                    overflowY="auto"
                  >
                    {result.output}
                  </Box>
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          )}
        </VStack>
      </CardBody>
    </Card>
  );
};

export default function LaunchDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();

  const { data: launch, isLoading, error } = useQuery(
    ['launch', id],
    () => launchAPI.getLaunch(id),
    {
      refetchInterval: (data) => {
        // Stop polling if workflow is completed or failed
        if (data?.status === 'completed' || data?.status === 'failed') {
          return false;
        }
        // Poll every 10 seconds for in-progress workflows
        return 10000;
      },
      refetchIntervalInBackground: false, // Don't poll when tab is not active
    }
  );

  const handleStartWorkflow = async () => {
    try {
      await launchAPI.startWorkflow(id);
      toast({
        title: 'Workflow started',
        description: 'The launch workflow has been initiated.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start workflow.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDeleteLaunch = async () => {
    if (window.confirm('Are you sure you want to delete this launch and all its data? This action cannot be undone.')) {
      try {
        await launchAPI.deleteLaunch(id);
        toast({
          title: 'Launch deleted',
          description: 'The launch and all its data have been deleted.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/');
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to delete launch.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      }
    }
  };

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading launch details...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          Failed to load launch: {error.message}
        </Alert>
      </Container>
    );
  }

  if (!launch) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="warning">
          <AlertIcon />
          Launch not found
        </Alert>
      </Container>
    );
  }

  const completedAgents = launch.agent_results.filter(r => r.status === 'completed').length;
  const totalAgents = launch.agent_results.length; // Dynamic count based on actual agents
  const progressPercentage = totalAgents > 0 ? (completedAgents / totalAgents) * 100 : 0;

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <HStack justify="space-between">
          <HStack spacing={4}>
            <Button
              as={RouterLink}
              to="/"
              variant="outline"
              leftIcon={<FiArrowLeft />}
            >
              Back to Dashboard
            </Button>
            <VStack align="start" spacing={1}>
              <Heading>{launch.name}</Heading>
              <HStack>
                <StatusBadge status={launch.status} />
                <Text fontSize="sm" color="gray.600">
                  Created: {new Date(launch.created_at).toLocaleDateString()}
                </Text>
              </HStack>
            </VStack>
          </HStack>
          <HStack spacing={2}>
            {launch.status === 'pending' && (
              <Button
                colorScheme="brand"
                leftIcon={<FiPlay />}
                onClick={handleStartWorkflow}
              >
                Start Workflow
              </Button>
            )}
            <Button
              colorScheme="red"
              variant="outline"
              leftIcon={<FiTrash2 />}
              onClick={handleDeleteLaunch}
            >
              Delete Launch
            </Button>
          </HStack>
        </HStack>

        <Card>
          <CardHeader>
            <Heading size="md">Workflow Progress</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Progress
                value={progressPercentage}
                size="lg"
                colorScheme="brand"
                width="full"
              />
              <Text fontSize="sm" color="gray.600">
                {completedAgents} of {totalAgents} agents completed
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Box>
          <Heading size="md" mb={4}>Agent Results</Heading>
          {launch.agent_results && launch.agent_results.length > 0 ? (
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
              {launch.agent_results.map((result) => (
                <AgentResultCard key={result.id} result={result} />
              ))}
            </SimpleGrid>
          ) : (
            <Alert status="info">
              <AlertIcon />
              No agent results yet. Start the workflow to begin processing.
            </Alert>
          )}
        </Box>

        {launch.summary && (
          <Card>
            <CardHeader>
              <Heading size="md">Launch Summary</Heading>
            </CardHeader>
            <CardBody>
              <Text whiteSpace="pre-wrap">{launch.summary}</Text>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Container>
  );
}

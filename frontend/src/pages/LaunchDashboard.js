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
  useToast,
} from '@chakra-ui/react';
import { useQuery } from 'react-query';
import { Link as RouterLink } from 'react-router-dom';
import { FiPlay, FiEye, FiClock, FiCheckCircle, FiXCircle } from 'react-icons/fi';
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

const LaunchCard = ({ launch }) => {
  const toast = useToast();

  const handleStartWorkflow = async () => {
    try {
      await launchAPI.startWorkflow(launch.id);
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

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">{launch.name}</Heading>
          <StatusBadge status={launch.status} />
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack align="start" spacing={3}>
          <Text fontSize="sm" color="gray.600">
            Created: {new Date(launch.created_at).toLocaleDateString()}
          </Text>
          {launch.summary && (
            <Text fontSize="sm" noOfLines={3}>
              {launch.summary}
            </Text>
          )}
          <HStack spacing={2}>
            <Button
              as={RouterLink}
              to={`/launches/${launch.id}`}
              size="sm"
              variant="outline"
              leftIcon={<FiEye />}
            >
              View Details
            </Button>
            {launch.status === 'pending' && (
              <Button
                size="sm"
                colorScheme="brand"
                leftIcon={<FiPlay />}
                onClick={handleStartWorkflow}
              >
                Start Workflow
              </Button>
            )}
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default function LaunchDashboard() {
  const { data: launches, isLoading, error } = useQuery(
    'launches',
    launchAPI.getLaunches,
    {
      refetchInterval: 15000, // Refetch every 15 seconds for real-time updates
      refetchIntervalInBackground: false, // Don't poll when tab is not active
    }
  );

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading launches...</Text>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          Failed to load launches: {error.message}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <HStack justify="space-between">
          <Heading>Launch Dashboard</Heading>
          <Button
            as={RouterLink}
            to="/launches/new"
            colorScheme="brand"
            leftIcon={<FiPlay />}
          >
            Create New Launch
          </Button>
        </HStack>

        {launches && launches.length > 0 ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {launches.map((launch) => (
              <LaunchCard key={launch.id} launch={launch} />
            ))}
          </SimpleGrid>
        ) : (
          <Box textAlign="center" py={12}>
            <Text fontSize="lg" color="gray.600" mb={4}>
              No launches found. Create your first launch to get started!
            </Text>
            <Button
              as={RouterLink}
              to="/launches/new"
              colorScheme="brand"
              size="lg"
            >
              Create Launch
            </Button>
          </Box>
        )}
      </VStack>
    </Container>
  );
}
